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


from supervisor.web import MeldView


# exchange class for images
class StatsImage(object):

    def __init__(self):
        self.contents = None

    def getNewImage(self):
        if self.contents:
            self.contents.close()
        from io import BytesIO
        self.contents = BytesIO()
        return self.contents

addressImageContents = StatsImage()
processImageContents = StatsImage()


# simple handlers for web images
class AddressImageView(MeldView):
    def render(self):
        # export internal memory buffer
        if addressImageContents.contents:
            return addressImageContents.contents.getvalue()
        return self.clone().write_xhtmlstring()

class ProcessImageView(MeldView):
    def render(self):
        # export internal memory buffer
        if processImageContents.contents:
            return processImageContents.contents.getvalue()
        return self.clone().write_xhtmlstring()

