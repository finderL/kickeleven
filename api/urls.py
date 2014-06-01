#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2011-9-12

@author: nttdocomo
'''
import web
from view import PublicApi, Upload

urls = ('', 'PublicApi',
        '/upload','Upload')

app_api = web.application(urls, locals())