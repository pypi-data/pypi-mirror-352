*** Settings ***
Documentation     Test suite for getLLM functionality
Library           Process
Library           OperatingSystem
Library           String
Library           Collections

*** Variables ***
${MOCK_FLAG}     --mock
${TEMP_DIR}      ${CURDIR}/temp
${INPUT_FILE}    ${TEMP_DIR}/input.txt

*** Test Cases ***
Test getLLM Installation
    [Documentation]    Verify getLLM is installed and accessible
    ${result}=    Run Process    which    getllm
    Should Be Equal As Integers    ${result.rc}    0    getLLM is not installed
    Log    getLLM is installed at: ${result.stdout}

Test Hugging Face Model Search
    [Documentation]    Test searching for Bielik models in Hugging Face
    Create Directory    ${TEMP_DIR}
    Create File    ${INPUT_FILE}    search-hf\nbielik\nexit
    ${result}=    Run Process    cat ${INPUT_FILE} | getllm ${MOCK_FLAG} -i    shell=True
    Should Contain    ${result.stdout}    bielik    msg=Bielik model not found in Hugging Face search
    [Teardown]    Remove Directory    ${TEMP_DIR}    recursive=True

Test Ollama Search With Hugging Face Fallback
    [Documentation]    Test Ollama search with fallback to Hugging Face for "bie" query
    Create Directory    ${TEMP_DIR}
    Create File    ${INPUT_FILE}    search-ollama\nbie\nexit
    ${result}=    Run Process    cat ${INPUT_FILE} | getllm ${MOCK_FLAG} -i    shell=True
    Should Contain Any    ${result.stdout}    Searching Hugging Face GGUF models    Found Hugging Face GGUF models    msg=Hugging Face fallback not triggered
    [Teardown]    Remove Directory    ${TEMP_DIR}    recursive=True

Test Model Installation Workflow
    [Documentation]    Test the model installation workflow
    Create Directory    ${TEMP_DIR}
    Create File    ${INPUT_FILE}    list\nexit
    ${result}=    Run Process    cat ${INPUT_FILE} | getllm ${MOCK_FLAG} -i    shell=True
    Should Contain    ${result.stdout}    available models    msg=Available models not listed
    [Teardown]    Remove Directory    ${TEMP_DIR}    recursive=True

Test Direct Code Generation
    [Documentation]    Test direct code generation capability
    ${result}=    Run Process    getllm ${MOCK_FLAG} "Write a hello world program in Python"    shell=True
    Should Contain    ${result.stdout}    print    msg=Code generation failed to produce Python code

*** Keywords ***
Should Contain Any
    [Arguments]    ${text}    @{substrings}    ${msg}=None of the expected substrings were found
    FOR    ${substring}    IN    @{substrings}
        ${status}=    Run Keyword And Return Status    Should Contain    ${text}    ${substring}
        Return From Keyword If    ${status}    ${TRUE}
    END
    Fail    ${msg}
