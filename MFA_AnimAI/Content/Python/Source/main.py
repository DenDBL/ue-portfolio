# -*- coding: utf-8 -*-

import os
import sys

ROOT_DIR = os.path.normpath(os.path.join(__file__, '../..'))
DLL_DIR = os.path.join(ROOT_DIR, 'DLLs')

sys.path.append(ROOT_DIR)
sys.path.append(DLL_DIR)

import Source.ui.app as app

if __name__ == '__main__':


    app.run()