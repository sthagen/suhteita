*** Settings ***
Library    Collections
Library    suhteita.robot.TicketSystemLibrary

*** Variables ***
${URL}    %{SUHTEITA_BASE_URL}
${USER}=   %{SUHTEITA_USER}
${PASS}    %{SUHTEITA_TOKEN}
${PROJECT}  overwrite-me-per-commandline
@{ISSUE_PATHS}=    key    id    self    fields/summary    fields/description    fields/updated

*** Test Cases ***
Connect To Ticket System
    ${session}    Ticket Session    ${URL}    ${USER}    ${PASS}

Connect To Ticket System And Retrieve Server Info
    ${session}    Ticket Session    ${URL}    ${USER}    ${PASS}
    ${server_info}    Get Server Info    ${session}    True
    Log Dictionary    ${server_info}    INFO

Connect To Ticket System And List Project Keys
    ${session}    Ticket Session    ${URL}    ${USER}    ${PASS}
    ${projects}    Projects    ${session}
    @{project_keys}=     Extract Project Keys    ${projects}
    Log List    ${project_keys}    INFO

Connect To Ticket System And Load Issue
    ${session}    Ticket Session    ${URL}    ${USER}    ${PASS}
    ${issue}=    Issue    ${session}    ${PROJECT}-42
    ${fields_of_interest}=    Extract Paths    ${issue}    ${ISSUE_PATHS}
    Log Dictionary    ${fields_of_interest}    INFO
    Log Dictionary    ${issue}    DEBUG
