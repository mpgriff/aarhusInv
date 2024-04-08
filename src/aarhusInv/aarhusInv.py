# -*- coding: utf-8 -*-
"""
Created on Sun Apr  7 16:56:49 2024

@author: au701230
"""

import numpy as np
import os
import subprocess
import time
import glob
import pandas as pd


class Model:

    def __init__(self, inv_dir, exe='AarhusInv64_v10.1.exe'):
        self.models = []
        self.inv_dir = inv_dir
        self.exe = exe

        if os.path.isfile(os.path.join(self.inv_dir, self.exe)) is False:

            print(self.exe + ' not found in ' + self.inv_dir + '.')

    def createModel(self, rhos, depths):
        if len(rhos) != len(depths) + 1:

            print('Number of depths should be 1 less than rhos, model will be skipped.')

        else:

            model = {}
            model['n_layers'] = len(rhos)

            if type(rhos) == list:
                rhos = np.array(rhos)

            if type(depths) == list:
                depths = np.array(depths)

            if sorted(depths) != depths.tolist():
                print('Depths need to be ascending, model will be skipped.')

            else:
                model['rhos'] = rhos
                model['depths'] = depths
                model['thicknesses'] = np.diff(np.insert(depths, 0, 0))

                self.models.append(model)

    def writeModFile(self, tem_file, mod_file='my_mod.mod', analysis=True):

        self.mod_file = mod_file

        n_soundings = len(self.models)

        if os.path.isfile(os.path.join(self.inv_dir, tem_file)) is False:

            print(tem_file + ' was not found in inv_dir.')
            print(mod_file + ' was not created.')

        else:

            mod_file_path = os.path.join(self.inv_dir, mod_file)

            f = open(mod_file_path, 'w+')

            # Write file header
            f.write('%s %s \n' % ('My mod file', '!Model name'))

            f.write('%s %d \t %d \t\t\t %s \n' % ('', n_soundings, 0,
                                                  '!#DataFiles, Constraints mode: 0->none, 1->vert, >=2-> vert+horiz'))

            for i in range(n_soundings):
                f.write('%s %d \t %d %s %s \n' % (' ', i+1, 1, tem_file, 
                                                  '!ModelNr, ParameterLayout, data file name'))

            if analysis:
                n_iter = 0
            else:
                n_iter = 1

            f.write('%s %d \t\t\t\t %s \n' % (' ', n_iter,
                                              '!Number of iterations: -1->Forward, 0->Analysis, >1->Number of Iterations'))

            for j, model in enumerate(self.models):

                f.write('%s %d \t\t\t %s \n' % (' ', model['n_layers'],
                                                '!# Number of layers, Model ' + str(j+1)))

                for i in range(model['n_layers']):

                    f.write('\t %.2f \t -1  \t %s \n' % (model['rhos'][i],
                                                         '!Resistivity ' + str(i+1)))
                for i in range(model['n_layers']-1):

                    f.write('\t %.2f \t -1 \t %s \n' % (model['thicknesses'][i],
                                                        '!Thickness ' + str(i+1)))

                for i in range(model['n_layers']-1):

                    f.write('\t %.2f \t -1 \t %s \n' % (
                                                        model['depths'][i],
                                                        '!Depths ' + str(i+1)))

            f.close()

            print(mod_file + ' has been created.')

    def runInv(self, mod_file=None):

        if mod_file is None:
            mod_file = self.mod_file

        cwd = os.getcwd()
        os.chdir(self.inv_dir)
        t = time.time()
        print('AarhusInv - Started')
        subprocess.run(self.exe + ' ' + mod_file, stdout=subprocess.PIPE)
        print('AarhusInv - Done')
        elapsed = time.time() - t
        print('Elapsed time is ' + str(np.round(elapsed, 2)) + ' seconds.')
        os.chdir(cwd)

    def getFileList(self, path, extension):

        if '.' in extension:
            extension = extension.replace('.', '')

        return glob.glob(path + '/*.' + extension)

    def readFWR(self, fwr_name, n_header_lines):

        fwr_df = pd.read_csv(os.path.join(self.inv_dir, fwr_name),
                             skiprows=n_header_lines, sep='\s+', header=None)

        return fwr_df

    def readTEM(self, tem_name, n_header_lines):

        tem_df = pd.read_csv(os.path.join(self.inv_dir, tem_name),
                             skiprows=n_header_lines, sep='\s+', header=None)

        return tem_df
