import yaml
import subprocess
from glob import glob
import os
import logging

from .i18n import localise
from .utils import run_and_save_logs
from .utils_ros import parse_tests_results
from .parameters import TMP_RUNTIME_PARAMS_YAML, TMP_SCENARIO_PARAMS_YAML

logging.basicConfig(level=logging.INFO)


def generate_scenario_parameter_output(params: dict, param_file: str) -> None:
    """
    Write `params` in `param_file` as YAML format
    (supports namespace nesting via forward slashes)
    roslaunch will then load them
    """
    with open(param_file, "w") as f:
        yaml.dump(params, f)


def generate_runtime_parameter_output(params: dict, param_file: str) -> None:
    """
    Write `params` in `param_file` as YAML format
    A strict dump is performed to avoid ambiguity:
    whatever the user specifies in artefacts.yaml/runtime/params will be made available in param_file
    """
    with open(param_file, "w") as f:
        yaml.dump(params, f)


def generate_rosbag_args(scenario: dict) -> str:
    if "rosbag_record" in scenario.keys():
        rosbag_record = scenario["rosbag_record"]
    else:
        # default behavior: do not record any rosbag
        rosbag_record = "none"

    # return the rosbag args as a string with the proper format
    if rosbag_record == "none":
        return "none"
    elif rosbag_record == "all":
        return "--all"
    elif rosbag_record == "subscriptions":
        if "subscriptions" in scenario.keys():
            sub = scenario["subscriptions"]
            topics = " ".join(list(sub.values()))
            return topics
        else:
            logging.warning(
                localise(
                    "[warning in generate_rosbag_args] rosbag_record asks for 'subscriptions' but they are not specified. Falling back to default: no rosbag will be recorded"
                )
            )
            return "none"
    else:
        assert type(rosbag_record) is list, (
            "rosbag_record supports 'all', 'none', 'subscriptions' or a list of strings interpreted as a list of ROS topics, regex supported"
        )
        for e in rosbag_record:
            assert type(e) is str, (
                "Elements of the rosbag_record list must only be strings. They are interpreted as a list of ROS topics, regex supported"
            )
        return f"--regex {' '.join(rosbag_record)}"


def get_result_path(scenario, PKGDIR, PACKAGE):
    """Can't choose the unittest output .xml filename with rostest.
    instead re-create here the hardcoded naming logic of rostest:
    need to find out the name of the test method
    """
    try:
        import rospkg
        import ast
        import xml.etree.ElementTree as ET

        # find the path of the user's launch file
        launch_file = (
            rospkg.RosPack().get_path(scenario["ros_testpackage"])
            + "/launch/"
            + scenario["ros_testfile"]
        )
        # find the user's test file and test package
        xml_root = ET.parse(launch_file).getroot()
        test_package = xml_root.find("test").get("pkg")
        test_file = xml_root.find("test").get("type")
        # find the path of the user's test file
        full_path = rospkg.RosPack().get_path(test_package) + "/src/" + test_file
        # parse the python file
        with open(full_path) as file:
            node = ast.parse(file.read())
        # find the class and method that match unittest convention naming (start with 'Test')
        # note: returns the first match
        test_class = [
            n for n in node.body if isinstance(n, ast.ClassDef) and "Test" in n.name
        ][0]
        test_class_suffix = test_class.name.split("Test")[-1].lower()
        # Finally, build the unittest result file path
        test_result_file_path = os.path.expanduser(
            f"{PKGDIR}/{PACKAGE}/rosunit-{test_class_suffix}.xml"
        )
        return test_result_file_path
    except Exception as e:
        logging.error(
            localise("[Exception in get_result_path()] {message}".format(message=e))
        )
        logging.error(
            localise(
                "Unable to parse the ros1 .launch specified ({testfile}) and the <test> tag within to find the unittest test method's name.".format(
                    testfile=scenario["ros_testfile"]
                )
            )
        )
        logging.error(
            localise(
                "Please ensure all ROS and unittest naming conventions are respected. Exiting.."
            )
        )
        return None


def get_wrapper_path():
    """Get the absolute path of artefacts_ros1_meta.launch wrapper inside our warp-client repo"""
    current_dir = os.path.abspath(os.path.dirname(__file__))
    wrapper_path = current_dir + "/wrappers/artefacts_ros1_meta.launch"
    return wrapper_path


def generate_sim_args(simulator_value, nosim_flag):
    if nosim_flag:
        return "none"
    else:
        return simulator_value


def run_ros1_tests(run):
    scenario = run.params
    job = run.job.params

    # ROS1 specific naming conventions for outputting results (can be chosen arbitrarily)
    PKGDIR = f"{os.path.expanduser(os.getenv('ROS_HOME', '~/.ros'))}/test_results"
    PACKAGE = "artefacts"

    # dump params specified by the user in the scenario section of the artefacts.yaml
    # to load them onto the rosparam server
    if "params" in scenario:
        param_file = TMP_SCENARIO_PARAMS_YAML  # note: fixed filename will lead concurent executions to overwrite each other
        generate_scenario_parameter_output(scenario["params"], param_file)
    else:
        param_file = "none"

    # dump params specified by the user in the runtime section of the artefacts.yaml
    # to make them available for the prelaunch script
    if "params" in job["runtime"]:
        # note: fixed filename will lead concurent executions to overwrite each other
        generate_runtime_parameter_output(
            job["runtime"]["params"], TMP_RUNTIME_PARAMS_YAML
        )

    # take note of previous rosbags
    rosbag_path = os.path.expanduser("~/.ros/*.bag")
    preexisting_rosbags = glob(rosbag_path)

    # get the unittest result path
    test_result_file_path = get_result_path(scenario, PKGDIR, PACKAGE)
    if test_result_file_path is None:
        return {}, False

    ## Main launch of the test sequence:
    # command line arguments control user specified settings for resource provisions
    # get_wrapper_path() is the absolute path of artefacts_ros1_meta.launch inside the warp-client repo
    command = [
        "rostest",
        get_wrapper_path(),
        "--package",
        PACKAGE,
        "--pkgdir",
        PKGDIR,
        f"rosbag_args:='{generate_rosbag_args(scenario)}'",
        f"simulator:={generate_sim_args(job['runtime']['simulator'], run.job.nosim)}",
        f"param_file:={param_file}",
        f"ros_testfile:={scenario['ros_testfile']}",
        f"ros_testpackage:={scenario['ros_testpackage']}",
    ]
    # for debugging: break rostest isolation from the host's ROSmaster
    if run.job.noisolation:
        command.insert(1, "--reuse-master")
    # last step to prepare the command for execution with subprocess.run():
    if "pre_launch" in job["runtime"].keys():
        # join the user's specified pre_launch command with the regular rostest command
        # note that a single subprocess.run() call is required for any environment variables sourced in the pre_launch command to be available for the rostest command
        command = f"{job['runtime']['pre_launch']} && {' '.join(command)}"
    else:
        command = " ".join(command)

    # Main: test execution
    # shell=True required to execute two commands in the same shell environment
    run_and_save_logs(
        command,
        shell=True,
        executable="/bin/bash",
        output_path=os.path.join(run.output_path, "test_process_log.txt"),
    )

    # parse xml generated by rostest
    results, success = parse_tests_results(test_result_file_path)

    # upload artefacts generated by rostest
    run.log_artifacts(os.path.expanduser(f"{PKGDIR}/{PACKAGE}"))

    # upload files from the general output folder
    run.log_artifacts(run.output_path)

    # upload any additional files in the folders specified by the user in artefacts.yaml
    for output in scenario.get("output_dirs", []):
        run.log_artifacts(output)

    # check if any rosbag was created
    rosbags = glob(rosbag_path)
    new_rosbags = set(rosbags).difference(set(preexisting_rosbags))
    if len(new_rosbags) > 0:
        new_rosbag = new_rosbags.pop()
        logging.info(
            localise("New rosbag found: {file_name}".format(file_name=new_rosbag))
        )
        # upload rosbag to dashboard
        run.log_single_artifact(new_rosbag, "rosbag")
        # perform any post processing, using the rosbag
        if "rosbag_postprocess" in scenario.keys():
            logging.info(localise("starting rosbag postprocess"))
            post_process_folder = os.path.expanduser(f"{PKGDIR}/{PACKAGE}_postprocess")
            os.makedirs(post_process_folder, exist_ok=True)
            existing_files = glob(f"{post_process_folder}/*")
            for f in existing_files:
                os.remove(f)
            command = [
                "rosrun",
                scenario["ros_testpackage"],
                scenario["rosbag_postprocess"],
                "--bag_path",
                f"{new_rosbag}",
                "--out_folder",
                f"{post_process_folder}",
            ]
            # shell=True required to support command list items that are strings with spaces
            # (allows passing additional arguments from the convenience of artefacts.yaml)
            subprocess.run(" ".join(command), shell=True, executable="/bin/bash")
            run.log_artifacts(post_process_folder)
            run.log_post_process_metrics(post_process_folder)

    run.log_tests_results(results, success)
    return results, success
