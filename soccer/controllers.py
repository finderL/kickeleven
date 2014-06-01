#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2014-1-23

@author: nttdocomo
'''
import web

class hello:
    def GET(self, name):
        render = web.template.render('templates')
        if not name:
            name = 'World'
        return render.index(name)