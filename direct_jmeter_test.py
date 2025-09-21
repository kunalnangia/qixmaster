#!/usr/bin/env python3
"""
Script to directly test JMeter functionality without going through the API
"""
import os
import sys
import subprocess
import shutil
from datetime import datetime
import uuid
import json

def find_jmeter():
    """Find JMeter executable"""
    print("Looking for JMeter...")
    
    # Option 1: Check JMETER_HOME environment variable
    jmeter_home = os.environ.get('JMETER_HOME')
    if jmeter_home and os.path.exists(jmeter_home):
        if os.name == 'nt':  # Windows
            jmeter_exec = os.path.join(jmeter_home, "bin", "jmeter.bat")
        else:  # Unix/Linux/Mac
            jmeter_exec = os.path.join(jmeter_home, "bin", "jmeter")
        
        if os.path.exists(jmeter_exec):
            print(f"✅ Found JMeter via JMETER_HOME: {jmeter_exec}")
            return jmeter_exec
    
    # Option 2: Check if jmeter is in PATH
    try:
        jmeter_in_path = shutil.which("jmeter")
        if jmeter_in_path:
            print(f"✅ Found JMeter in PATH: {jmeter_in_path}")
            return jmeter_in_path
    except Exception as e:
        print(f"❌ Error checking for JMeter in PATH: {e}")
    
    # Option 3: Look for jmeter.bat or jmeter in common locations
    possible_locations = [
        # Current directory
        os.path.join(os.getcwd(), "apache-jmeter-5.6.3", "bin", "jmeter.bat"),
        # Parent directory
        os.path.join(os.path.dirname(os.getcwd()), "apache-jmeter-5.6.3", "bin", "jmeter.bat"),
        # Root of project
        os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), "apache-jmeter-5.6.3", "bin", "jmeter.bat"),
    ]
    
    for location in possible_locations:
        if os.path.exists(location):
            print(f"✅ Found JMeter at: {location}")
            return location
    
    print("❌ JMeter not found")
    return None

def generate_test_plan(url="https://hostbooks.com", concurrent_users=5, duration=10, ramp_up=2):
    """Generate a simple JMeter test plan"""
    print(f"Generating test plan for URL: {url}")
    
    # Create template directory if it doesn't exist
    os.makedirs("test_templates", exist_ok=True)
    
    # Generate a unique template name
    template_name = f"test_templates/direct_test_{uuid.uuid4()}.jmx"
    
    # Parse URL components
    protocol = "https"
    domain = url
    path = "/"
    
    if "://" in url:
        url_parts = url.split("://")
        protocol = url_parts[0]
        remaining = url_parts[1]
        
        if "/" in remaining:
            domain_parts = remaining.split("/", 1)
            domain = domain_parts[0]
            path = "/" + domain_parts[1]
        else:
            domain = remaining
    
    # Basic JMeter test plan
    jmeter_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.2">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="Direct Test Plan" enabled="true">
      <stringProp name="TestPlan.comments"></stringProp>
      <boolProp name="TestPlan.functional_mode">false</boolProp>
      <boolProp name="TestPlan.tearDown_on_shutdown">true</boolProp>
      <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>
      <elementProp name="TestPlan.user_defined_variables" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" testname="User Defined Variables" enabled="true">
        <collectionProp name="Arguments.arguments"/>
      </elementProp>
      <stringProp name="TestPlan.user_define_classpath"></stringProp>
    </TestPlan>
    <hashTree>
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="Thread Group" enabled="true">
        <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
        <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="Loop Controller" enabled="true">
          <boolProp name="LoopController.continue_forever">false</boolProp>
          <intProp name="LoopController.loops">-1</intProp>
        </elementProp>
        <stringProp name="ThreadGroup.num_threads">{concurrent_users}</stringProp>
        <stringProp name="ThreadGroup.ramp_time">{ramp_up}</stringProp>
        <boolProp name="ThreadGroup.scheduler">true</boolProp>
        <stringProp name="ThreadGroup.duration">{duration}</stringProp>
        <stringProp name="ThreadGroup.delay">0</stringProp>
        <boolProp name="ThreadGroup.same_user_on_next_iteration">true</boolProp>
      </ThreadGroup>
      <hashTree>
        <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="HTTP Request" enabled="true">
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="User Defined Variables" enabled="true">
            <collectionProp name="Arguments.arguments"/>
          </elementProp>
          <stringProp name="HTTPSampler.domain">{domain}</stringProp>
          <stringProp name="HTTPSampler.port"></stringProp>
          <stringProp name="HTTPSampler.protocol">{protocol}</stringProp>
          <stringProp name="HTTPSampler.contentEncoding"></stringProp>
          <stringProp name="HTTPSampler.path">{path}</stringProp>
          <stringProp name="HTTPSampler.method">GET</stringProp>
          <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
          <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
          <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
          <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          <stringProp name="HTTPSampler.embedded_url_re"></stringProp>
          <stringProp name="HTTPSampler.connect_timeout"></stringProp>
          <stringProp name="HTTPSampler.response_timeout"></stringProp>
        </HTTPSamplerProxy>
        <hashTree/>
        <ResultCollector guiclass="ViewResultsFullVisualizer" testclass="ResultCollector" testname="View Results Tree" enabled="true">
          <boolProp name="ResultCollector.error_logging">false</boolProp>
          <objProp>
            <name>saveConfig</name>
            <value class="SampleSaveConfiguration">
              <time>true</time>
              <latency>true</latency>
              <timestamp>true</timestamp>
              <success>true</success>
              <label>true</label>
              <code>true</code>
              <message>true</message>
              <threadName>true</threadName>
              <dataType>true</dataType>
              <encoding>false</encoding>
              <assertions>true</assertions>
              <subresults>true</subresults>
              <responseData>false</responseData>
              <samplerData>false</samplerData>
              <xml>false</xml>
              <fieldNames>true</fieldNames>
              <responseHeaders>false</responseHeaders>
              <requestHeaders>false</requestHeaders>
              <responseDataOnError>false</responseDataOnError>
              <saveAssertionResultsFailureMessage>true</saveAssertionResultsFailureMessage>
              <assertionsResultsToSave>0</assertionsResultsToSave>
              <bytes>true</bytes>
              <sentBytes>true</sentBytes>
              <url>true</url>
              <threadCounts>true</threadCounts>
              <idleTime>true</idleTime>
              <connectTime>true</connectTime>
            </value>
          </objProp>
          <stringProp name="filename"></stringProp>
        </ResultCollector>
        <hashTree/>
      </hashTree>
    </hashTree>
  </hashTree>
</jmeterTestPlan>"""
    
    # Save the template to a file
    with open(template_name, "w") as f:
        f.write(jmeter_template)
    
    print(f"✅ Test plan saved to: {template_name}")
    return template_name

def run_jmeter_test(jmx_file, jmeter_cmd):
    """Run JMeter test and return results file"""
    print(f"Running JMeter test with file: {jmx_file}")
    
    # Create results directory
    run_id = str(uuid.uuid4())[:8]
    results_dir = f"direct_results/{run_id}"
    os.makedirs(results_dir, exist_ok=True)
    results_file = os.path.join(results_dir, "results.csv")
    report_dir = os.path.join(results_dir, "report")
    
    # Build command
    cmd = [jmeter_cmd, "-n", "-t", jmx_file, "-l", results_file, "-e", "-o", report_dir]
    
    print(f"Executing command: {' '.join(cmd)}")
    
    try:
        # Run JMeter
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Check result
        if result.returncode == 0:
            print("✅ JMeter test completed successfully")
            print(f"Results saved to: {results_file}")
            print(f"Report generated at: {report_dir}")
            
            # Print stdout
            print("\nCommand Output:")
            print(result.stdout)
            
            return results_file, report_dir
        else:
            print("❌ JMeter test failed")
            print(f"Exit code: {result.returncode}")
            print(f"Error output: {result.stderr}")
            return None, None
    except Exception as e:
        print(f"❌ Error running JMeter: {e}")
        return None, None

def main():
    """Main function"""
    print("=" * 60)
    print("Direct JMeter Test")
    print("=" * 60)
    print(f"Current time: {datetime.now()}")
    print(f"Current directory: {os.getcwd()}")
    print()
    
    # Find JMeter
    jmeter_cmd = find_jmeter()
    if not jmeter_cmd:
        print("❌ JMeter not found. Cannot proceed with test.")
        return
    
    # Generate test plan
    jmx_file = generate_test_plan(
        url="https://hostbooks.com", 
        concurrent_users=5,
        duration=10,
        ramp_up=2
    )
    
    # Run test
    results_file, report_dir = run_jmeter_test(jmx_file, jmeter_cmd)
    
    if results_file and report_dir:
        print("\n" + "=" * 60)
        print("JMeter Test Summary")
        print("=" * 60)
        
        # Check if results file exists
        if os.path.exists(results_file):
            print(f"✅ Results file exists: {results_file}")
            
            # Try to read and parse results
            try:
                with open(results_file, 'r') as f:
                    lines = f.readlines()
                    if len(lines) > 1:
                        print(f"✅ Results file contains {len(lines)} lines")
                        print(f"Headers: {lines[0].strip()}")
                    else:
                        print("⚠️ Results file is empty or contains only headers")
            except Exception as e:
                print(f"❌ Error reading results file: {e}")
        else:
            print(f"❌ Results file does not exist: {results_file}")
        
        # Check if report directory exists
        if os.path.exists(report_dir):
            print(f"✅ Report directory exists: {report_dir}")
            
            # Check if index.html exists
            index_html = os.path.join(report_dir, "index.html")
            if os.path.exists(index_html):
                print(f"✅ Report index.html exists: {index_html}")
            else:
                print(f"❌ Report index.html does not exist: {index_html}")
        else:
            print(f"❌ Report directory does not exist: {report_dir}")
        
        print("\nTest completed successfully")
    else:
        print("\nTest failed")

if __name__ == "__main__":
    main()