"""Load the JIRA instance."""
import argparse
import datetime as dti
import json
import secrets

import suhteita.actions as actions
from suhteita import (
    APP_ALIAS,
    APP_ENV,
    BASE_URL,
    IDENTITY,
    IS_CLOUD,
    NODE_INDICATOR,
    PROJECT,
    STORE,
    TOKEN,
    TS_FORMAT_PAYLOADS,
    USER,
    extract_fields,
    log,
    two_sentences,
)
from suhteita.store import Store


def main(options: argparse.Namespace, version: str = 'UNKNOWN') -> int:
    """Drive the transactions."""

    # Belt and braces:
    user = options.user if options.user else USER
    target_url = options.target_url if options.target_url else BASE_URL
    is_cloud = options.is_cloud if options.is_cloud else IS_CLOUD
    target_project = options.target_project if options.target_project else PROJECT
    scenario = options.scenario if options.scenario else 'unknown'
    identity = options.identity if options.identity else IDENTITY
    storage_path = options.out_path if options.out_path else STORE

    has_failures = False

    if not TOKEN:
        log.error(f'No secret token or pass phrase given, please set {APP_ENV}_TOKEN accordingly')
        return 2

    log.info('=' * 84)
    log.info(f'Generator {APP_ALIAS} version {version}')
    log.info('# Prelude of a 27-steps scenario test execution')

    c_rand, d_rand = two_sentences()
    log.info(f'- Setup <01> Random sentence of original ({c_rand})')
    log.info(f'- Setup <02> Random sentence of duplicate ({d_rand})')

    random_component = secrets.token_urlsafe()
    log.info(f'- Setup <03> Random component name ({random_component})')

    todo, in_progress, done = ('to do', 'in progress', 'done')
    log.info(f'- Setup <04> The test workflow assumes the (case insensitive) states ({todo}, {in_progress}, {done})')

    ts = dti.datetime.now(tz=dti.timezone.utc).strftime(TS_FORMAT_PAYLOADS)
    log.info(f'- Setup <05> Timestamp marker in summaries will be ({ts})')

    desc_core = '... and short description we dictate.'
    log.info(f'- Setup <06> Common description part - of twin issues / pair - will be ({desc_core})')

    amendment = 'No, no, no. They duplicated me, help!'
    log.info(f'- Setup <07> Amendment for original description will be ({amendment})')

    fake_comment = 'I am the original, surely!'
    log.info(f'- Setup <08> Fake comment for duplicate will be ({fake_comment})')

    duplicate_labels = ['du', 'pli', 'ca', 'te']
    log.info(f'- Setup <09> Labels for duplicate will be ({duplicate_labels})')

    original_labels = ['for', 'real', 'highlander']
    log.info(f'- Setup <10> Labels for original will be ({original_labels})')

    hours_value = 42
    log.info(f'- Setup <11> Hours value for original estimate will be ({hours_value})')

    purge_me = 'SUHTEITA_PURGE_ME_ORIGINAL'
    log.info(f'- Setup <12> Purge indicator comment will be ({purge_me})')

    node_indicator = NODE_INDICATOR
    log.info(f'- Setup <13> Node indicator ({node_indicator})')
    log.info(
        f'- Setup <14> Connect will be to upstream ({"cloud" if is_cloud else "on-site"}) service ({target_url})'
        f' per login ({user})'
    )
    log.info('-' * 84)

    # Here we start the timer for the session:
    start_time = dti.datetime.now(tz=dti.timezone.utc)
    start_ts = start_time.strftime(TS_FORMAT_PAYLOADS)
    context = {
        'target': target_url,
        'mode': f'{"cloud" if is_cloud else "on-site"}',
        'project': target_project,
        'scenario': scenario,
        'identity': identity,
        'start_time': start_time,
    }
    store = Store(context=context, folder_path=storage_path)
    log.info(f'# Starting 27-steps scenario test execution at at ({start_ts})')
    log.info('- Step <01> LOGIN')
    clk, service = actions.login(target_url, user, password=TOKEN, is_cloud=is_cloud)
    log.info(f'^ Connected to upstream service; CLK={clk}')
    store.add('LOGIN', True, clk)

    log.info('- Step <02> SERVER_INFO')
    clk, server_info = actions.get_server_info(service)
    log.info(f'^ Retrieved upstream server info cf. [SRV]; CLK={clk}')
    store.add('SERVER_INFO', True, clk, str(server_info))

    log.info('- Step <03> PROJECTS')
    clk, projects = actions.get_all_projects(service)
    log.info(f'^ Retrieved {len(projects)} unarchived projects; CLK={clk}')
    store.add('PROJECTS', True, clk, f'count({len(projects)})')

    proj_env_ok = False
    if target_project:
        proj_env_ok = any((target_project == project['key'] for project in projects))

    if not proj_env_ok:
        log.error('Belt and braces - verify project selection:')
        log.info(json.dumps(sorted([project['key'] for project in projects]), indent=2))
        return 1

    first_proj_key = target_project if proj_env_ok else projects[0]['key']
    log.info(
        f'Verified target project from request ({target_project}) to be'
        f' {"" if proj_env_ok else "not "}present and set target project to ({first_proj_key})'
    )

    log.info('- Step <04> CREATE_ISSUE')
    clk, c_key = actions.create_issue(
        service, first_proj_key, ts, description=f'{c_rand}\n{desc_core}\nCAUSALITY={node_indicator}'
    )
    log.info(f'^ Created original ({c_key}); CLK={clk}')
    store.add('CREATE_ISSUE', True, clk, 'original')

    log.info('- Step <05> ISSUE_EXISTS')
    clk, c_e = actions.issue_exists(service, c_key)
    log.info(f'^ Existence of original ({c_key}) verified with result ({c_e}); CLK={clk}')
    store.add('ISSUE_EXISTS', bool(c_e), clk, 'original')

    log.info('- Step <06> CREATE_ISSUE')
    clk, d_key = actions.create_issue(
        service, first_proj_key, ts, description=f'{d_rand}\n{desc_core}\nCAUSALITY={node_indicator}'
    )
    log.info(f'^ Created duplicate ({d_key}); CLK={clk}')
    store.add('CREATE_ISSUE', True, clk, 'duplicate')

    log.info('- Step <07> ISSUE_EXISTS')
    clk, d_e = actions.issue_exists(service, d_key)
    log.info(f'^ Existence of duplicate ({d_key}) verified with result ({d_e}); CLK={clk}')
    store.add('ISSUE_EXISTS', bool(d_e), clk, 'duplicate')

    query = f'issue = {c_key}'
    log.info('- Step <08> EXECUTE_JQL')
    clk, c_q = actions.execute_jql(service=service, query=query)
    log.info(f'^ Executed JQL({query}); CLK={clk}')
    store.add('EXECUTE_JQL', True, clk, f'query({query.replace(c_key, "original-key")})')

    log.info('- Step <09> AMEND_ISSUE_DESCRIPTION')
    clk = actions.amend_issue_description(service, c_key, amendment=amendment, issue_context=c_q)
    log.info(f'^ Amended description of original {d_key} with ({amendment}); CLK={clk}')
    store.add('AMEND_ISSUE_DESCRIPTION', True, clk, 'original')

    log.info('- Step <10> ADD_COMMENT')
    clk, _ = actions.add_comment(service=service, issue_key=d_key, comment=fake_comment)
    log.info(f'^ Added comment ({fake_comment}) to duplicate {d_key}; CLK={clk}')
    store.add('ADD_COMMENT', True, clk, 'duplicate')

    log.info('- Step <11> UPDATE_ISSUE_FIELD')
    clk = actions.update_issue_field(service, d_key, labels=duplicate_labels)
    log.info(f'^ Updated duplicate {d_key} issue field of labels to ({duplicate_labels}); CLK={clk}')
    store.add('UPDATE_ISSUE_FIELD', True, clk, 'duplicate')

    log.info('- Step <12> UPDATE_ISSUE_FIELD')
    clk = actions.update_issue_field(service, c_key, labels=original_labels)
    log.info(f'^ Updated original {c_key} issue field of labels to ({original_labels}); CLK={clk}')
    store.add('UPDATE_ISSUE_FIELD', True, clk, 'original')

    log.info('- Step <13> CREATE_DUPLICATES_ISSUE_LINK')
    clk, _ = actions.create_duplicates_issue_link(service, c_key, d_key)
    log.info(f'^ Created link on duplicate stating it duplicates the original; CLK={clk}')
    store.add('CREATE_DUPLICATES_ISSUE_LINK', True, clk, 'dublicate duplicates original')

    log.info('- Step <14> GET_ISSUE_STATUS')
    clk, d_iss_state = actions.get_issue_status(service, d_key)
    d_is_todo = d_iss_state.lower() == todo
    log.info(
        f'^ Retrieved status of the duplicate {d_key} as ({d_iss_state})'
        f' with result (is_todo == {d_is_todo}); CLK={clk}'
    )
    store.add('GET_ISSUE_STATUS', d_is_todo, clk, f'duplicate({d_iss_state})')

    log.info('- Step <15> SET_ISSUE_STATUS')
    clk, _ = actions.set_issue_status(service, d_key, in_progress)
    log.info(f'^ Transitioned the duplicate {d_key} to ({in_progress}); CLK={clk}')
    store.add('SET_ISSUE_STATUS', True, clk, f'duplicate ({todo})->({in_progress})')

    log.info('- Step <16> SET_ISSUE_STATUS')
    clk, _ = actions.set_issue_status(service, d_key, done)
    log.info(f'^ Transitioned the duplicate {d_key} to ({done}); CLK={clk}')
    store.add('SET_ISSUE_STATUS', True, clk, f'duplicate ({in_progress})->({done})')

    log.info('- Step <17> GET_ISSUE_STATUS')
    clk, d_iss_state_done = actions.get_issue_status(service, d_key)
    d_is_done = d_iss_state_done.lower() == done
    log.info(
        f'^ Retrieved status of the duplicate {d_key} as ({d_iss_state_done})'
        f' with result (d_is_done == {d_is_done}); CLK={clk}'
    )
    store.add('GET_ISSUE_STATUS', d_is_done, clk, f'duplicate({d_iss_state_done})')

    log.info('- Step <18> ADD_COMMENT')
    clk, response_step_18_add_comment = actions.add_comment(service, d_key, 'Closed as duplicate.')
    log.info(f'^ Added comment on {d_key} with response extract cf. [RESP-STEP-18]; CLK={clk}')
    store.add('ADD_COMMENT', True, clk, f'duplicate({response_step_18_add_comment["body"]})')

    log.info('- Step <19> SET_ORIGINAL_ESTIMATE')
    clk, ok = actions.set_original_estimate(service, c_key, hours=hours_value)
    log.info(f'^ Added ({hours_value}) hours as original estimate to original {c_key} with result ({ok}); CLK={clk}')
    store.add('SET_ORIGINAL_ESTIMATE', ok, clk, 'original')

    log.info('- Step <20> GET_ISSUE_STATUS')
    clk, c_iss_state = actions.get_issue_status(service, c_key)
    c_is_todo = c_iss_state.lower() == todo
    log.info(
        f'^ Retrieved status of the original {c_key} as ({c_iss_state})'
        f' with result (c_is_todo == {c_is_todo}); CLK={clk}'
    )
    store.add('GET_ISSUE_STATUS', c_is_todo, clk, f'original({c_iss_state})')

    log.info('- Step <21> SET_ISSUE_STATUS')
    clk, _ = actions.set_issue_status(service, c_key, in_progress)
    log.info(f'^ Transitioned the original {c_key} to ({in_progress}); CLK={clk}')
    store.add('SET_ISSUE_STATUS', True, clk, f'original ({todo})->({in_progress})')

    log.info('- Step <22> GET_ISSUE_STATUS')
    clk, c_iss_state_in_progress = actions.get_issue_status(service, c_key)
    c_is_in_progress = c_iss_state_in_progress.lower() == in_progress
    log.info(
        f'^ Retrieved status of the original {c_key} as ({c_iss_state_in_progress})'
        f' with result (c_is_in_progress == {c_is_in_progress}); CLK={clk}'
    )
    store.add('GET_ISSUE_STATUS', c_is_in_progress, clk, f'original({c_iss_state_in_progress})')

    log.info('- Step <23> CREATE_COMPONENT')
    clk, comp_id, a_component, comp_resp = actions.create_component(
        service=service, project=first_proj_key, name=random_component, description=c_rand
    )
    log.info(f'^ Created component ({a_component}) with response extract cf. [RESP-STEP-23]; CLK={clk}')
    store.add('CREATE_COMPONENT', True, clk, f'component({comp_resp["description"]})')  # type: ignore

    log.info('- Step <24> RELATE_ISSUE_TO_COMPONENT')
    clk, ok = actions.relate_issue_to_component(service, c_key, comp_id, a_component)
    log.info(
        f'^ Attempted relation of original {c_key} issue to component ({a_component}) with result ({ok}); CLK={clk}'
    )
    store.add('RELATE_ISSUE_TO_COMPONENT', ok, clk, 'original')
    if not ok:
        has_failures = True

    log.info('- Step <25> LOAD_ISSUE')
    clk, x_iss = actions.load_issue(service, c_key)
    log.info(f'^ Loaded issue {c_key}; CLK={clk}')
    log.debug(json.dumps(x_iss, indent=2))
    store.add('LOAD_ISSUE', True, clk, 'original')

    log.info('- Step <26> ADD_COMMENT')
    clk, response_step_26_add_comment = actions.add_comment(service=service, issue_key=c_key, comment=purge_me)
    log.info(f'^ Added purge tag comment on original {c_key} with response extract cf. [RESP-STEP-26]; CLK={clk}')
    store.add('ADD_COMMENT', True, clk, f'original({response_step_26_add_comment["body"]})')

    log.info('- Step <27> ADD_COMMENT')
    clk, response_step_27_add_comment = actions.add_comment(service=service, issue_key=d_key, comment=purge_me)
    log.info(
        f'^ Added purge tag comment on duplicate issue {d_key} with response extract cf. [RESP-STEP-27]; CLK={clk}'
    )
    store.add('ADD_COMMENT', True, clk, f'duplicate({response_step_27_add_comment["body"]})')

    # Here we stop the timer for the session:
    end_time = dti.datetime.now(tz=dti.timezone.utc)
    end_ts = end_time.strftime(TS_FORMAT_PAYLOADS)
    log.info(f'# Ended execution of 27-steps scenario test at ({end_ts})')
    log.info(f'Execution of 27-steps scenario test took {(end_time - start_time)} h:mm:ss.uuuuuu')
    log.info('-' * 84)

    log.info('# References:')
    log.info(f'[SRV]          Server info is ({server_info})')
    log.info(
        f'[RESP-STEP-18] Add comment response is'
        f' ({extract_fields(response_step_18_add_comment, fields=("self", "body"))})'
    )
    log.info(
        f'[RESP-STEP-23] Create component response is ({extract_fields(comp_resp, fields=("self", "description"))})'
    )
    log.info(
        f'[RESP-STEP-26] Add comment response is'
        f' ({extract_fields(response_step_26_add_comment, fields=("self", "body"))})'
    )
    log.info(
        f'[RESP-STEP-27] Add comment response is'
        f' ({extract_fields(response_step_27_add_comment, fields=("self", "body"))})'
    )
    log.info('-' * 84)

    log.info('Dumping records to store...')
    store.dump(end_time=end_time, has_failures=has_failures)
    log.info('-' * 84)

    log.info('OK')
    log.info('=' * 84)

    return 0
