#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2014-1-23

@author: nttdocomo
'''
import web

class hello:
    def GET(self, name):
        session = web.config.session
        render = web.template.render('templates', globals={'login': hasattr(session, 'login') and session.login})
        return render.index()