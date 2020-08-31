from datetime import datetime
from os import listdir
import os
import re
import json
import shutil
import pandas as pd
from application_logging.logger import App_Logger

class bulkdatavalidation:

    def __init__(self, path):
        self.Batch_Directory = "static/uploads"
        self.schema_path = 'schema_prediction.json'
        self.logger = App_Logger()

    def valuesFromSchema(self):
        try:
            with open(self.schema_path, 'r') as f:
                dic = json.load(f)
                f.close()
            pattern = dic['SampleFileName']
            column_names = dic['ColName']
            NumberofColumns = dic['NumberofColumns']
            file = open("predicttion/valuesfromSchemaValidationLog.txt", 'a+')
            message = "NumberofColumns:: %s" % NumberofColumns + "\n"
            self.logger.log(file, message)
            file.close()
        except ValueError:
            file = open("predicttion/valuesfromSchemaValidationLog.txt", 'a+')
            self.logger.log(file, "ValueError:Value not found inside schema_prediction.json")
            file.close()
            raise ValueError
        except KeyError:
            file = open("predicttion/valuesfromSchemaValidationLog.txt", 'a+')
            self.logger.log(file, "KeyError:Key value error incorrect key passed")
            file.close()
            raise KeyError
        except Exception as e:
            file = open("predicttion/valuesfromSchemaValidationLog.txt", 'a+')
            self.logger.log(file, str(e))
            file.close()
            raise e
        return column_names, NumberofColumns


    def manualRegexCreation(self):
        regex = "['InputFile'].csv"
        return regex
    def validationFileNameRaw(self,regex):
        onlyfiles = [f for f in listdir(self.Batch_Directory)]

        try:

            f = open("predicttion/nameValidationLog.txt", 'a+')
            for filename in onlyfiles:
                if (re.match(regex, filename)):
                    self.logger.log(f,"Valid File name!! File name :: %s" % filename)
                else:
                    self.logger.log(f, "Invalid File Name!! file name should be InputFile  :: %s" % filename)

            f.close()

        except Exception as e:
            f = open("predicttion/nameValidationLog.txt", 'a+')
            self.logger.log(f, "Error occured while validating FileName %s" % e)
            f.close()
            raise e
    def validateColumnLength(self,NumberofColumns):
        try:
            f = open("predicttion/columnValidationLog.txt", 'a+')
            self.logger.log(f,"Column Length Validation Started!!")
            for file in listdir('static/uploads/'):
                csv = pd.read_csv('static/uploads/' + file)

                if csv.shape[1] == NumberofColumns:
                    pass
                else:
                   self.logger.log(f, "Invalid Column Length for the file!!  :: %s" % file)
            self.logger.log(f, "Column Length Validation Completed!!")
        except OSError:
            f = open("predicttion/columnValidationLog.txt", 'a+')
            self.logger.log(f, "Error Occured while moving the file :: %s" % OSError)
            f.close()
            raise OSError
        except Exception as e:
            f = open("predicttion/columnValidationLog.txt", 'a+')
            self.logger.log(f, "Error Occured:: %s" % e)
            f.close()
            raise e
        f.close()

    def getdata(self):
        pred_file=pd.read_csv('static/uploads/InputFile.csv')
        return  pred_file