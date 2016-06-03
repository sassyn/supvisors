#!/usr/bin/python
#-*- coding: utf-8 -*-

# ======================================================================
# Copyright 2016 Julien LE CLEACH
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ======================================================================

from supervisors.options import mainOptions as opt

from supervisor.datatypes import boolean, list_of_strings

# XSD contents for XML validation
from StringIO import StringIO
XSDContents = StringIO('''\
<xs:schema attributeFormDefault="unqualified" elementFormDefault="qualified" xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:simpleType name="Loading">
        <xs:restriction base="xs:int">
            <xs:minInclusive value="0"/>
            <xs:maxInclusive value="100"/>
        </xs:restriction>
    </xs:simpleType>
    <xs:complexType name="ProgramModel">
        <xs:choice>
            <xs:element type="xs:string" name="reference"/>
            <xs:sequence>
                <xs:element type="xs:string" name="addresses" minOccurs="0" maxOccurs="1"/>
                <xs:element type="xs:byte" name="sequence" minOccurs="0" maxOccurs="1"/>
                <xs:element type="xs:boolean" name="required" minOccurs="0" maxOccurs="1"/>
                <xs:element type="xs:boolean" name="wait_exit" minOccurs="0" maxOccurs="1"/>
                <xs:element type="Loading" name="expected_loading" minOccurs="0" maxOccurs="1"/>
            </xs:sequence>
        </xs:choice>
        <xs:attribute type="xs:string" name="name" use="required"/>
    </xs:complexType>
    <xs:complexType name="ApplicationModel">
        <xs:sequence>
            <xs:element type="xs:boolean" name="autostart" minOccurs="0" maxOccurs="1"/>
            <xs:choice minOccurs="0" maxOccurs="unbounded">
                <xs:element type="ProgramModel" name="program"/>
                <xs:element type="ProgramModel" name="pattern"/>
            </xs:choice>
        </xs:sequence>
        <xs:attribute type="xs:string" name="name" use="required"/>
    </xs:complexType>
    <xs:element name="root">
        <xs:complexType>
            <xs:sequence>
                <xs:choice minOccurs="0" maxOccurs="unbounded">
                    <xs:element type="ProgramModel" name="model"/>
                    <xs:element type="ApplicationModel" name="application"/>
                </xs:choice>
            </xs:sequence>
        </xs:complexType>
    </xs:element>
</xs:schema>
''')

class _Parser(object):
    def setFilename(self, filename):
        self._tree = self._parse(filename)
        self._root = self._tree.getroot()
        # get models
        elements = self._root.findall("./model[@name]")
        self._models = { element.get('name'): element for element in elements }
        opt.logger.debug(self._models)
        # get patterns
        elements = self._root.findall(".//pattern[@name]")
        self._patterns = { element.get('name'): element for element in elements }
        opt.logger.debug(self._patterns)

    def setApplicationRules(self, application):
        # find application element
        opt.logger.trace('searching application element for {}'.format(application.applicationName))
        applicationElement = self._root.find("./application[@name='{}']".format(application.applicationName))
        if applicationElement is not None:
            # get rules
            value = applicationElement.findtext('autostart')
            application.rules.autostart = boolean(value) if value else False
            opt.logger.info('application {} - rules {}'.format(application.applicationName, application.rules))

    def setProcessRules(self, process):
        opt.logger.trace('searching program element for {}'.format(process.getNamespec()))
        programElement = self._getProgramElement(process)
        if programElement is not None:
            # get addresses rule
            self._getProgramAddresses(programElement, process.rules)
            # get sequence rule
            value = programElement.findtext('sequence')
            process.rules.sequence = int(value) if value and int(value)>=0 else -1
            # get required rule
            value = programElement.findtext('required')
            process.rules.required = boolean(value) if value else False
            # get wait_exit rule
            value = programElement.findtext('wait_exit')
            process.rules.wait_exit = boolean(value) if value else False
            # get expected_loading rule
            value = programElement.findtext('expected_loading')
            process.rules.expected_loading = int(value) if value and 0<=int(value)<=100 else 1
        opt.logger.debug('process {} - rules {}'.format(process.getNamespec(), process.rules))

    def _getProgramAddresses(self, programElement, rules):
        value = programElement.findtext('addresses')
        if value:
            # sort and trim
            from collections import OrderedDict
            addresses = list(OrderedDict.fromkeys(filter(None, list_of_strings(value))))
            from supervisors.addressmapper import addressMapper
            rules.addresses = [ '*' ] if '*' in addresses else addressMapper.getExpectedAddresses(addresses)

    def _getProgramElement(self, process):
        # try to find program name in file
        programElement = self._root.find("./application[@name='{}']/program[@name='{}']".format(process.applicationName, process.processName))
        opt.logger.trace('{} - direct search program element {}'.format(process.getNamespec(), programElement))
        if programElement is None:
            # try to find a corresponding pattern
            patterns = [ name for name, element in self._patterns.items() if name in process.getNamespec() ]
            opt.logger.trace('{} - found patterns {}'.format(process.getNamespec(), patterns))
            if patterns:
                pattern = max(patterns, key=len)
                programElement = self._patterns[pattern]
            opt.logger.trace('{} - pattern search program element {}'.format(process.getNamespec(), programElement))
        if programElement is not None:
            # find if model referenced in element
            model = programElement.findtext('reference')
            if model in self._models.keys():
                programElement = self._models[model]
            opt.logger.trace('{} - model search ({}) program element {}'.format(process.getNamespec(), model, programElement))
        return programElement

    def _parse(self, filename):
        self._parser = None
        # find parser
        try:
            from lxml import etree
            opt.logger.info('using lxml.etree parser')
            # parse XML and validate it
            tree = etree.parse(filename)
            # get XSD
            schemaDoc = etree.parse(XSDContents)
            schema = etree.XMLSchema(schemaDoc)
            xmlValid = schema.validate(tree)
            if xmlValid:
                opt.logger.info('XML validated')
            else:
                opt.logger.error('XML NOT validated: {0}'.format(filename))
                import sys
                print >> sys.stderr,  schema.error_log
            return tree if xmlValid else None
        except ImportError:
            try:
                from xml.etree import ElementTree
                opt.logger.info('using xml.etree.ElementTree parser')
                return ElementTree.parse(filename)
            except ImportError:
                opt.logger.critical("Failed to import ElementTree from any known place")
                raise


parser = _Parser()

# unit test expecting that a Supervisor Server is running at address below
if __name__ == "__main__":
    from xml.etree import ElementTree
    tree = ElementTree.parse('/home/cliche/python/DISTRIB/etc/deployment.xml')
    root = tree.getroot()
    # get models
    elements = root.findall("./model[@name]")
    print elements
    for element in elements:
        print element, element.get('name')
    models = { element.get('name'): element for element in elements }
    print models