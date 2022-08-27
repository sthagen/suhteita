*** Settings ***
Library    Collections
Library    suhteita.robot.TicketSystemLibrary

*** Variables ***
${URL}    %{SUHTEITA_BASE_URL}
${USER}=   %{SUHTEITA_USER}
${PASS}    %{SUHTEITA_TOKEN}
${PROJECT}  overwrite-me-per-commandline
@{FIELDS}=    key    id    self
@{PROJECT_FIELDS}=    key    id

*** Test Cases ***
Connect To JIRA
    ${session}    Ticket Session    ${URL}    ${USER}    ${PASS}
    ${projects}    Projects    ${session}
    FOR    ${project}    IN     @{projects}
        ${DATA}=    Extract Fields    ${project}   ${PROJECT_FIELDS}
    END
Load Issue
    ${session}    Ticket Session    ${URL}    ${USER}    ${PASS}
    ${issue}=    Issue    ${session}    ${PROJECT}-42
    ${fields_of_interest}=    Extract Fields    ${issue}    ${FIELDS}
    Log Dictionary    ${issue}    INFO
