# -----------------------------------------------------------------------------
# This script contains functions which are used
# to communicate with Opal RT through the RT-Lab
# Python API. The Python API is used to compile
# a model, load the model, and execute a model.
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
#  Import modules
# -----------------------------------------------------------------------------
## Import OpalApi module for Python
import RtlabApi
from time import sleep
import os
import sys
from datetime import datetime
import logging as log

log.basicConfig(filename='OPALRTFMU.log', filemode='w',
                level=log.DEBUG, format='%(asctime)s %(message)s',
                datefmt='%m/%d/%Y %I:%M:%S %p')
stderrLogger = log.StreamHandler()
stderrLogger.setFormatter(log.Formatter(log.BASIC_FORMAT))
log.getLogger().addHandler(stderrLogger)

def resetModel(projectPath, reset):
    """
    Function to force reset of running OPAL-RT model.

    This function is used to force a reset of the model.
    This is just for manually testing that resetting the model
    will trigger a recompilation. Otherwise we will have to
    log off and log on to trigger recompilation.
    This function will be removed in production code.

    :param projectPath: Path to the project file
    :param reset: Flag to activate a reset of the model

    """

    if (reset):
        projectName = os.path.abspath(projectPath)
        log.info("=====Path to the project={!s}".format(projectName))

        ## Open a model using its name.
        RtlabApi.OpenProject(projectName)
        log.info ("=====The connection with {!s} is completed.".format(projectName))

        ## Get the model state and the real time mode
        modelState, realTimeMode = RtlabApi.GetModelState()

        ## Print the model state
        log.info ("=====The model state is {!s}.".format(RtlabApi.OP_MODEL_STATE(modelState)))

        ## If the model is running
        if modelState == RtlabApi.MODEL_RUNNING:
            #print("This is the output value={!s}".format(RtlabApi.GetSignalsByName('sm_computation.reference_out')))
            ## Pause the model
            log.info ("=====The model is running and will be reset.")
            ctlr = 1
            RtlabApi.GetSystemControl (ctlr)
            RtlabApi.Reset()
            ctlr = 0
            RtlabApi.GetSystemControl (ctlr)
            # Return an internal defined code to avoid recompilation.
            RtlabApi.Disconnect()
        return -2222

def compileAndInstantiate(projectPath):
    """
    Function to compile, load, and execute a model.

    :param projectPath: Path to the project file.

    """

    # Check if MetaController is running and if not start it up

    import subprocess
    # Start the MetaController
    tasklist = subprocess.check_output('tasklist', shell=True)
    if not "MetaController.exe" in tasklist:
        log.info("=====Starting the MetaController.")
        try:
            subprocess.Popen("MetaController")
        except:
            log.error("=====MetaController.exe couldn't be started. ")
            log.error("=====Check that the \\common\\bin folder of RT-Lab is on the system PATH.")
            raise

        log.info("=====MetaController is successfully started.")

    # Wait 1 second to give time to the MetaController to start
    sleep(1.0)
    projectName = os.path.abspath(projectPath)
    log.info("=====Path to the project={!s}".format(projectName))

    ## Open a model using its name.
    RtlabApi.OpenProject(projectName)
    log.info ("=====The connection with {!s} is completed.".format(projectName))

    # Check if model was already compiled and is already running
    try:
        ## Get the model state and the real time mode
        modelState, realTimeMode = RtlabApi.GetModelState()

        ## Print the model state
        log.info ("=====The model state is {!s}.".format(RtlabApi.OP_MODEL_STATE(modelState)))

        ## If the model is running
        if modelState == RtlabApi.MODEL_RUNNING:
            #print("This is the output value={!s}".format(RtlabApi.GetSignalsByName('sm_computation.reference_out')))
            ## Pause the model
            log.info ("=====The model is running and won't be recompiled.")
            # Return an internal defined code to avoid recompilation.
            RtlabApi.Disconnect()
            return -1111

    except Exception:
        ## Ignore error 11 which is raised when
        ## RtlabApi.DisplayInformation is called whereas there is no
        ## pending message
        info = sys.exc_info()
        if info[1][0] != 11:  # 'There is currently no data waiting.'
            ## If a exception occur: stop waiting
            log.error ("=====An error occured during compilation.")
            #raise

    start = datetime.now()

    mdlFolder, mdlName = RtlabApi.GetCurrentModel()
    mdlPath = os.path.join(mdlFolder, mdlName)

    try:
        ## Registering this thread to receive all messages from the controller
        ## (used to display compilation log into python console)
        RtlabApi.RegisterDisplay(RtlabApi.DISPLAY_REGISTER_ALL)

        ## Set attribute on project to force to recompile (optional)
        modelId = RtlabApi.FindObjectId(RtlabApi.OP_TYPE_MODEL, mdlPath)
        RtlabApi.SetAttribute(modelId, RtlabApi.ATT_FORCE_RECOMPILE, True)

        ## Launch compilation
        compilationSteps = RtlabApi.OP_COMPIL_ALL_NT | RtlabApi.OP_COMPIL_ALL_LINUX
        RtlabApi.StartCompile2((("", compilationSteps), ), )
        log.info ("=====Compilation started.")

        ## Wait until the end of the compilation
        status = RtlabApi.MODEL_COMPILING
        while status == RtlabApi.MODEL_COMPILING:
            try:
                ## Check status every 0.5 second
                sleep(0.5)

                ## Get new status
                ## To be done before DisplayInformation because
                ## DisplayInformation may generate an Exception when there is
                ## nothing to read
                status, _ = RtlabApi.GetModelState()

                ## Display compilation log into Python console
                _, _, msg = RtlabApi.DisplayInformation(1)
                while len(msg) > 0:
                    log.info (msg),
                    _, _, msg = RtlabApi.DisplayInformation(1)

            except Exception:
                ## Ignore error 11 which is raised when
                ## RtlabApi.DisplayInformation is called whereas there is no
                ## pending message
                info = sys.exc_info()
                if info[1][0] != 11:  # 'There is currently no data waiting.'
                    ## If a exception occur: stop waiting
                    log.error ("=====An error occured during compilation.")
                    raise

        ## Because we use a comma after print when forward compilation log into
        ## Python log we have to ensure to write a carriage return when
        ## finished.
        log.info('')

        ## Get project status to check is compilation succeed
        status, _ = RtlabApi.GetModelState()
        if status == RtlabApi.MODEL_LOADABLE:
            log.info ("=====Compilation success.")
        else:
            log.error ("=====Compilation failed.")

        ## Load the current model
        realTimeMode = RtlabApi.HARD_SYNC_MODE  # Also possible to use SIM_MODE, SOFT_SIM_MODE, SIM_W_NO_DATA_LOSS_MODE or SIM_W_LOW_PRIO_MODE
        timeFactor   = 1
        RtlabApi.Load(realTimeMode, timeFactor)
        log.info ("=====The model is loaded.")

        try:
            # Get an write the signal in the models
            log.info("=====The signal description of the model={!s}".format(RtlabApi.GetSignalsDescription()))

            ## Execute the model
            RtlabApi.Execute(timeFactor)
            log.info ("=====The model executes for the first time.")

        except Exception:
            ## Ignore error 11 which is raised when
            ## RtlabApi.DisplayInformation is called whereas there is no
            ## pending message
            info = sys.exc_info()
            if info[1][0] != 11:  # 'There is currently no data waiting.'
                ## If a exception occur: stop waiting
                log.error ("An error occured during execution.")
                raise

        end = datetime.now()
        log.info(
            '=====Compiled, loaded and executed the model for the first time in {!s} seconds.'.format(
                (end - start).total_seconds()))
    finally:
        ## Always disconnect from the model when the connection is completed
        log.info ("=====The model has been successfully compiled and is now running.")
        RtlabApi.Disconnect()

def setData(projectPath, inputNames, inputValues, simulationTime):
    """
    Function to exchange data with a running model.

    :param projectPath: Path to the project file.
    :param inputNames: Input signal names of the  model.
    :param inputValues: Input signal values of the  model.
    :param simulationTime: Model simulation time.

    """

    # Wait prior to setting the inputs
    sleep (0.5)
    projectName = os.path.abspath(projectPath)
    #log.info("=====Path to the project={!s}".format(projectName))

    start = datetime.now()
    RtlabApi.OpenProject(projectName)

    if (simulationTime < RtlabApi.GetStopTime() or RtlabApi.GetStopTime() <= 0.0):
        #log.info ("=====The connection with {!s} is completed.".format(projectName))
        try:
            ## Get the model state and the real simulationTime mode
            modelState, realTimeMode = RtlabApi.GetModelState()

            ## Print the model state
            #log.info ("=====The model state is {!s}.".format(RtlabApi.OP_MODEL_STATE(modelState)))

            ## If the model is running
            if modelState == RtlabApi.MODEL_RUNNING:
                ## Set input data
                ########Setting inputs of the model
                try:
                    #signalNames = (signalName1, signalName2, ...)
                    #signalValues = (value1, value2, ...)
                    #RtlabApi.SetSignalsByName(signalNames, signalValues)
                    ## Get signal control before changing values
                    ctlr = 1
                    RtlabApi.GetSystemControl (ctlr)
                    #log.info ("=====The system control is acquired.")
                    RtlabApi.GetSignalControl(ctlr)
                    #log.info ("=====The signal control is acquired.")
                    RtlabApi.Pause()
                    #log.info ("=====The model is paused.")
                    RtlabApi.SetSignalsByName(inputNames, inputValues)
                    #log.info ("=====The signals are set.")
                    timeFactor   = 1
                    RtlabApi.Execute(timeFactor)
                    #log.info ("=====The model is executed.")
                    ## Release signal control after changing values
                    ctlr = 0
                    RtlabApi.GetSignalControl(ctlr)
                    #log.info ("=====The signal control is released.")
                    RtlabApi.GetSystemControl (ctlr)
                    #log.info ("=====The system control is released.")

                except Exception:
                    ## Ignore error 11 which is raised when
                    ## RtlabApi.DisplayInformation is called whereas there is no
                    ## pending message
                    info = sys.exc_info()
                    if info[1][0] != 11:  # 'There is currently no data waiting.'
                        ## If a exception occur: stop waiting
                        log.error ("=====An error occured at simulationTime={!s} while setting the " \
                               "input values for the input names={!s}.".format(simulationTime, inputNames))
                        raise
            ## if the model is not running
            else:
                ## Print the model state
                log.error ("=====The model state is not running. Simulation will be terminated.")
                raise
            end = datetime.now()
            log.info(
                '=====Send values={!s} of inputs with names={!s} in {!s} seconds.'.format(inputValues,
                inputNames, (end - start).total_seconds()))
        finally:
            ## Always disconnect from the model when the connection
            RtlabApi.Disconnect()
    else:
        RtlabApi.Disconnect()
        log.info ("=====The simulation stoptime={!s} is reached. "\
               " the connection is closed.".format(RtlabApi.GetStopTime()))


def getData(projectPath, outputNames, simulationTime):
    """
    Function to exchange data with a running model.

    :param projectPath: Path to the project file.
    :param outputNames: Output signal names of the  model.
    :param simulationTime: Model simulation time.

    """

    # Wait prior to getting the outputs
    sleep(1.0)

    ## Connect to a running model using its name.
    projectName = os.path.abspath(projectPath)
    #log.info("=====Path to the project={!s}".format(projectName))

    start = datetime.now()
    RtlabApi.OpenProject(projectName)

    if (simulationTime < RtlabApi.GetStopTime() or RtlabApi.GetStopTime() <= 0.0):

        #log.info ("=====The connection with {!s} is completed.".format(projectName))
        try:
            ## Get the model state and the real simulationTime mode
            modelState, realTimeMode = RtlabApi.GetModelState()

            ## Print the model state
            #log.info ("=====The model state is {!s}.".format(RtlabApi.OP_MODEL_STATE(modelState)))

            ## If the model is running
            if modelState == RtlabApi.MODEL_RUNNING:
                ## Exchange data
                try:
                    ctlr = 1
                    RtlabApi.GetSystemControl (ctlr)
                    #log.info ("=====The system control is acquired.")
                    RtlabApi.Pause()
                    #log.info ("=====The model is paused.")
                    outputValues = RtlabApi.GetSignalsByName(outputNames)
                    timeFactor   = 1
                    RtlabApi.Execute(timeFactor)
                    #log.info ("=====The model is executed.")
                    ## Release signal control after changing values
                    ctlr = 0
                    RtlabApi.GetSystemControl (ctlr)
                    #log.info ("=====The system control is released.")
                except Exception:
                    ## Ignore error 11 which is raised when
                    ## RtlabApi.DisplayInformation is called whereas there is no
                    ## pending message
                    info = sys.exc_info()
                    if info[1][0] != 11:  # 'There is currently no data waiting.'
                        ## If a exception occur: stop waiting
                        log.error ("=====An error occured at simulationTime={!s} while getting the " \
                               "output values for the output names={!s}.".format(simulationTime, outputNames))
                        raise

            ## if the model is not running
            else:
                ## Print the model state
                log.error ("=====The model is not running. Simulation will be terminated.")
                raise

            end = datetime.now()
            log.info(
                '=====Get values={!s} of outputs with names={!s} in {!s} seconds.'.format(outputValues,
                outputNames, (end - start).total_seconds()))
        finally:
            ## Always disconnect from the model when the connection
            ## is completed
            RtlabApi.Disconnect()
        return outputValues
    else:
        ctlr = 1
        #RtlabApi.GetSystemControl (ctlr)
        #RtlabApi.Reset()
        ctlr = 0
        #RtlabApi.GetSystemControl (ctlr)
        RtlabApi.Disconnect()
        log.info ("=====The simulation stoptime={!s} is reached. "\
               "The model is reset and the connection is closed.".format(RtlabApi.GetStopTime()))
        return zeroOutputValues (outputNames)


def zeroOutputValues(outputNames):
    """
    Function returns a zero output scalar or vector.

    :param outputNames: List of output names

    """
    if (isinstance(outputNames, list)):
        retOutputValues = [0.0] * len (outputNames)
    else:
        retOutputValues = 0.0
    return retOutputValues

def convertUnicodeString(inputNames):

    """
    Function gets unicode string and converts it to a string.

    :param outputNames: List of input names

    """
    retNames = []
    if (isinstance(inputNames, list)):
        for elem in inputNames:
            retNames.append(str(elem))
    else:
        retNames = str(inputNames)

    return retNames


def exchange(projectPath, simulationTime, inputNames, inputValues, outputNames, writeResults):

#if __name__ == "__main__":

    ## Connect to a running model using its name.
    #projectName = os.path.abspath(os.path.join('examples', 'demo', 'demo.llp'))

     """
     Function to exchange data with the Opal RT FMU.

     :param projectPath: Path to the project file.
     :param simulationTime: Model simulation time.
     :param inputNames: Input signal names of the  model.
     :param inputValues: Input signal values of the  model.
     :param outputNames: Output signal names of the  model.
     :param outputValues: Output signal values of the  model.
     :param writeResults: Flag to write results.

     """

     # Convert the unicode string to a string
     projectPath = convertUnicodeString(projectPath)

     # This is just for testing and will be retrieved from the project path
     # The section below will be removed in production code
     ######################################################
     reset = 0
     retVal = resetModel (projectPath, reset)
     if retVal == -2222:
       return zeroOutputValues(outputNames)
     # Convert the input and output names to be strings that can be set in Opal-RT models
     #inputNames = 'demo/sc_user_interface/port1'
     #inputNames = None
     #inputValues = 1.0
     #outputNames = ['demo/sm_computation/port1', 'demo/sm_computation/port2', 'demo/sm_computation/port3']
     ######################################################
     if (inputNames is not None):
         inputNames=convertUnicodeString(inputNames)
     if (outputNames is not None):
        outputNames=convertUnicodeString(outputNames)

     log.info ("=====Ready to compile, load, or execute the model.")
     # Compile and Run the model for the first time
     retVal = compileAndInstantiate(projectPath)
     if (retVal <> -1111):
        log.info ("=====The model hasn't been compiled yet.")
        return zeroOutputValues (outputNames)

     #simulationTime = 0.0
     log.info ("=====Ready to exchange data with the OPAL-RT running model.")
     # Handle the case when inputNames is None

     if(inputNames is not None):
         log.info ("=====Ready to set the input variables={!s} with values={!s} at time={!s}.".format(inputNames, inputValues, simulationTime))
         if (isinstance(inputNames, list)):
             len_inputNames = len(inputNames)
             len_inputValues = len(inputValues)
             if(len_inputNames<>len_inputValues):
                 log.error ("=====An error occured at simulationTime={!s}. "\
                         "Length of inputNames={!s} ({!s}) does not match " \
                         "length of input values={!s} ({!s}).".format(simulationTime, inputNames,
                         len_inputNames, inputValues, len_inputValues))
                 raise
             setData(projectPath, tuple(inputNames), tuple(inputValues), simulationTime)
         else:
             setData(projectPath, inputNames, inputValues, simulationTime)
         log.info("=====The input variables={!s} were successfully set.".format(inputNames))

     if (outputNames is not None):
         log.info ("=====Ready to get the output variables={!s} at time={!s}.".format(outputNames, simulationTime))
         if (isinstance(outputNames, list)):
             outputValues = getData(projectPath, tuple(outputNames), simulationTime)
             len_outputNames = len(outputNames)
             len_outputValues = len(outputValues)
             if(len_outputNames<>len_outputValues):
                 log.error ("=====An error occured at simulationTime={!s}. "\
                         "Length of outputNames={!s} ({!s}) does not match " \
                         "length of output values={!s} ({!s}).".format(simulationTime, outputNames,
                         len_outputNames, outputValues, len_outputValues))
                 raise
             outputValues = getData(projectPath, tuple(outputNames), simulationTime)
         else:
             outputValues = getData(projectPath, outputNames, simulationTime)
         log.info("=====The output variables={!s} were successfully retrieved.".format(outputNames))

         if(outputValues is None):
             log.error ("=====The output values for outputNames={!=} is empty at time={!s}.".
                    format(outputNames, simulationTime))
             raise
         log.info ("=====The values of the output variables:{!s} are equal {!s} at time={!s}.".format(outputNames,
                 outputValues, simulationTime))

     # Convert the output values to float so they can be used on the receiver side.
     retOutputValues = []
     if (isinstance(outputValues, tuple)):
         for elem in outputValues:
             retOutputValues.append(1.0*float(elem))
     else:
         retOutputValues = 1.0 * float (outputValues)

     return retOutputValues

#if __name__ == "__main__":

    ## Connect to a running model using its name.
    #projectName = os.path.abspath(os.path.join('examples', 'demo', 'demo.llp'))
