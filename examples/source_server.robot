*** Settings ***
Library    Collections
Library    suhteita.robot.SourceServerLibrary

*** Variables ***
${URL}    %{SUHTEITA_BASE_URL}
${USER}=   %{SUHTEITA_USER}
${PASS}    %{SUHTEITA_TOKEN}
${PROJECT}  ohne
@{ISSUE_PATHS}=    key    id    self    fields/summary    fields/description    fields/updated

*** Test Cases ***
Connect To Source Server
    ${session}    Source Session    ${URL}    ${USER}    ${PASS}

Connect To Source Server And Retrieve Server Info
    ${session}    Source Session    ${URL}    ${USER}    ${PASS}
    ${server_info}    Get Announcement_Banner    ${session}
    Log Dictionary    ${server_info}    INFO

Connect To Source Server And Verify The Special Project Exists
    ${session}    Source Session    ${URL}    ${USER}    ${PASS}
    ${is_present}=    Project Exists    ${session}     ${PROJECT}

Connect To Source Server And List Project Keys
    ${session}    Source Session    ${URL}    ${USER}    ${PASS}
    ${projects}    Project List    ${session}
    @{project_keys}=     Extract Project Keys    ${projects}
    Log List    ${project_keys}    INFO

Connect To Source Server And List Repos of the special Project
    ${session}    Source Session    ${URL}    ${USER}    ${PASS}
    ${repos}    Repo List    ${session}    ${PROJECT}    0    25
    @{repo_keys}=     Extract Project Keys    ${repos}
    Log List    ${repo_keys}    INFO
