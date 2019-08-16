# import modules
import time
import os
import sqlite3
import pandas as pd
import abtas
import warnings
warnings.filterwarnings('ignore')
# set script parameters
site = 'T01'                                                               # what is the site/receiver ID?
recType = 'lotek'                                                          # what is the receiver type?
proj_dir = r'J:\1210\005\Calcs\Studies\3_3_19\2019'                   # what is the project directory?
dbName = 'ultrasound_2019.db'                                         # what is the name of the project database 
# optional orion parameters if receivers used switching
scanTime = 2.0
channels = 2
ant_to_rec_dict = {1:'T02',2:'T03'}
# set up workspaces   
file_dir = os.path.join(proj_dir,'Data','Training_Files')
files = os.listdir(file_dir)
projectDB = os.path.join(proj_dir,'Data',dbName)
scratch_dir = os.path.join(proj_dir,'Output','Scratch')
figure_ws = os.path.join(proj_dir,'Output','Figures')
print ("There are %s files to iterate through"%(len(files)))
tS = time.time()                                                           # what time is it? for script performanceg    
# if orion receivers do not employ switching use:                                                          
abtas.telemDataImport(site,recType,file_dir,projectDB) 
# if orion recievers use swtiching use:
abtas.telemDataImport(site,recType,file_dir,projectDB, switch = True, scanTime = scanTime, channels = channels, ant_to_rec_dict = ant_to_rec_dict) 
# get the fish to iterate through using SQL 
conn = sqlite3.connect(projectDB)
c = conn.cursor()
sql = "SELECT tblRaw.FreqCode FROM tblRaw LEFT JOIN tblMasterTag ON tblRaw.FreqCode = tblMasterTag.FreqCode WHERE recID == '%s' AND TagType IS NOT 'Study' AND TagType IS NOT 'Test';"%(site)
histories = pd.read_sql_query(sql,con = conn).FreqCode.unique()
c.close()
print ("Finished importing data and indexing database, there are %s fish to iterate through" %(len(histories)))
print ("Creating training objects for every fish at site %s"%(site))   
print ("This will take a while")
print ("Grab a coffee, call your mother.") 
# create list of training data objects to iterate over with a Pool multiprocess
iters = []
for i in histories:
    iters.append(abtas.training_data(i,site,projectDB,scratch_dir))
print ("history objects created")
for i in iters:
    abtas.calc_train_params_map(i)  
print ("Telemetry Parameters Quantified, appending data to project database")
abtas.trainDatAppend(scratch_dir,projectDB)    
print ("process took %s to compile"%(round(time.time() - tS,3)))
train_stats = abtas.classification_results(recType,projectDB,figure_ws,site)
train_stats.train_stats() 