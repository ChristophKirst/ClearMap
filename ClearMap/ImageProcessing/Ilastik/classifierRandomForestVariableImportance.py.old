from classifierBase import *
import warnings
import numpy
import vigra
#from PyQt4.QtGui import QInputDialog
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import h5py

#*******************************************************************************
# C l a s s i f i e r R a n d o m F o r e s t V a r i a b l e I m p o r t a n c e *
#*******************************************************************************

class ClassifierRandomForestVariableImportance(ClassifierBase):
    #human readable information
    name = "Random forest classifier with variable importance" 
    description = "Random forest classifier with computation of variable importance"
    author = "HCI, University of Heidelberg"
    homepage = "http://hci.iwr.uni-heidelberg.de"

    #minimum required isotropic context
    #0 means pixel based classification
    #-1 means whole dataset
    minContext = 0
    treeCount = 100

    def __init__(self):
        ClassifierBase.__init__(self)
        self.oob = 0
        self.variableImportance = numpy.zeros( (1, ) )
        
    @classmethod
    def settings(cls):
        #(number, ok) = QInputDialog.getInt(None, "Random Forest parameters", \
        #                                         "Number of trees (minimum 20, maximum 255)", \
        #                                          cls.treeCount, 20, 255)
        if ok:
            cls.treeCount = number
        print "setting number of trees to", cls.treeCount

    def train(self, features, labels, isInteractive):
        self.RF = None
        assert self.numWorkers > 0, "Need at least one worker. Use setWorker() method..."

        thisTreeCount = int(self.treeCount/self.numWorkers)
        if(self.workerNumber == self.numWorkers-1):
            thisTreeCount += int(self.treeCount % self.numWorkers)
        
        if features.shape[0] != labels.shape[0]:
            # #features != # labels"
            return

        if not labels.dtype == numpy.uint32:
            labels = labels.astype(numpy.uint32)
        if not features.dtype == numpy.float32:
            features = features.astype(numpy.float32)

        if labels.ndim == 1:
            labels.shape = labels.shape + (1,)
        
        self.unique_vals = numpy.unique(labels)
        
        # Have to set this becauce the new rf dont set mtry properly by default
        # mtry = max(1,int(numpy.sqrt(features.shape[1]))+1) 
        
        self.RF = vigra.learning.RandomForest(treeCount=thisTreeCount)
        if isInteractive:
            self.oob = self.RF.learnRF(features, labels)
            self.variableImportance = numpy.zeros( (1, ) )
        else:
            self.oob, self.variableImportance = self.RF.learnRFWithFeatureSelection(features, labels)
            ClassifierBase.printLock.acquire()
            a = self.variableImportance
            varStr = " ".join([str(i) + ": " + "%7.4f"%k for i,k in enumerate(a[:,-1])])
            print "Gini Importance: " + varStr
            ClassifierBase.printLock.release()
        
    def predict(self, features):
        #3d: check that only 1D data arrives here
        if self.RF is not None and features is not None and len(self.unique_vals) > 1:
            if not features.dtype == numpy.float32:
                features = numpy.array(features, dtype=numpy.float32)
            return self.RF.predictProbabilities(features)
        else:
            return None
        
    def serialize(self, fileName, pathInFile, overWriteFlag=False):
        # cannot serialize into group because can not pass h5py handle to vigra yet
        # works only with new RF version
        tmp = self.RF.writeHDF5(fileName, pathInFile, overWriteFlag)
        f = h5py.File(fileName, 'r+')
        f.create_dataset(pathInFile+'/Variable importance', data=self.variableImportance)
        f.create_dataset(pathInFile+'/OOB', data=self.oob)
        f.close()

    @classmethod
    def deserialize(cls, fileName, pathInFile):
        classifier = cls()
        classifier.RF = vigra.learning.RandomForest(fileName, pathInFile)
        classifier.treeCount = classifier.RF.treeCount
        return classifier



