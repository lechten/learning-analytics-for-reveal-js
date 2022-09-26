from dash import dcc
from dash import html
from django_plotly_dash import DjangoDash
from dash.dependencies import Input, Output, State
from Dashboard.models import Event, Session, Student, SlideSet, Course, DwellTime, TimePeriod, Quiz, SlideTransition, \
    Shortcut
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
import datetime
import logging
from datetime import time
from datetime import datetime
from django.utils import timezone
from django.db import connection

external_stylesheets = ['https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css']

# Important: Define Id for Plotly Dash integration in Django
app = DjangoDash('dashboard_app')
app.css.append_css({
    "external_url": external_stylesheets
})

"""
    Check if database exists and query all tables on page load
"""
all_tables = connection.introspection.table_names()
if all_tables:
    queryset_course = Course.objects.all()
    df_course = pd.DataFrame.from_records(queryset_course.values())

    queryset_dwell_time = DwellTime.objects.all()
    df_dwell_time = pd.DataFrame.from_records(queryset_dwell_time.values())

    queryset_events = Event.objects.all()
    df_event = pd.DataFrame.from_records(queryset_events.values())

    queryset_quiz_events = Quiz.objects.all()
    df_quiz_events = pd.DataFrame.from_records(queryset_quiz_events.values())

    queryset_shortcut_events = Shortcut.objects.all()
    df_shortcut_events = pd.DataFrame.from_records(queryset_shortcut_events.values())

    queryset_slide_transition_events = SlideTransition.objects.all()
    df_slide_transition_events = pd.DataFrame.from_records(queryset_slide_transition_events.values())

    queryset_TimePeriod = TimePeriod.objects.all()
    df_TimePeriod = pd.DataFrame.from_records(queryset_TimePeriod.values())

    queryset_slide_set = SlideSet.objects.all()
    df_slide_set = pd.DataFrame.from_records(queryset_slide_set.values())

    queryset_sessions = Session.objects.all()
    df_sessions = pd.DataFrame.from_records(queryset_sessions.values())


"""
    Update all data on button click "refresh" - execute DB queries again
"""
@app.callback(
    Output('last_update', 'children'),
    Input('refresh-data', 'n_clicks')
)
def refresh_data(value):
    global df_course, df_dwell_time, df_event, df_quiz_events, df_shortcut_events
    global df_slide_transition_events, df_TimePeriod, df_slide_set, df_sessions

    queryset_course = Course.objects.all()
    df_course = pd.DataFrame.from_records(queryset_course.values())

    queryset_dwell_time = DwellTime.objects.all()
    df_dwell_time = pd.DataFrame.from_records(queryset_dwell_time.values())

    queryset_events = Event.objects.all()
    df_event = pd.DataFrame.from_records(queryset_events.values())

    queryset_quiz_events = Quiz.objects.all()
    df_quiz_events = pd.DataFrame.from_records(queryset_quiz_events.values())

    queryset_shortcut_events = Shortcut.objects.all()
    df_shortcut_events = pd.DataFrame.from_records(queryset_shortcut_events.values())

    queryset_slide_transition_events = SlideTransition.objects.all()
    df_slide_transition_events = pd.DataFrame.from_records(queryset_slide_transition_events.values())

    queryset_TimePeriod = TimePeriod.objects.all()
    df_TimePeriod = pd.DataFrame.from_records(queryset_TimePeriod.values())

    queryset_slide_set = SlideSet.objects.all()
    df_slide_set = pd.DataFrame.from_records(queryset_slide_set.values())

    queryset_sessions = Session.objects.all()
    df_sessions = pd.DataFrame.from_records(queryset_sessions.values())

    return "Refreshed: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")


"""
    Serves the layout for the Dash app
"""
def serve_layout():
    ddl_course_options = [{'label': "All courses...", 'value': -1}]
    if not df_course.empty:
        ddl_course_options += [{'label': x, 'value': y} for x, y in
                               zip(df_course['name'], df_course['id'])]

    ddl_slide_set = [{'label': "All courses...", 'value': -1}]
    if not df_slide_set.empty:
        ddl_slide_set += [{'label': x, 'value': y} for x, y in
                          zip(df_slide_set['name'], df_slide_set['base_url'])]

    app_layout = html.Div([
        html.Div([
            dbc.Card([
                html.Div([
                    html.Div([
                        html.H5(children='Course:'),

                    ], className='col-1'),
                    html.Div([
                        dcc.Dropdown(id='ddl_course', clearable=False, options=ddl_course_options
                                     , placeholder='All courses...', value=-1),

                    ], className='col-2'),

                    html.Div([
                    ], className='col-6'),

                    html.Div([
                        html.Button('Refresh Data', id="refresh-data", className="btn btn-secondary"),
                    ], className='col-3')

                ], className='row pt-4 px-5'),
                html.Div([
                    html.Div([
                        html.H5(children='Set of slides:'),

                    ], className='col-1'),
                    html.Div([
                        dcc.Dropdown(id='ddl_slide_set', clearable=False,
                                     options=ddl_slide_set
                                     , placeholder='All slide sets...', value=-1),
                    ], className='col-2'),

                    html.Div([

                    ], className='col-6'),

                    html.Div([
                        html.Div(id='last_update')
                    ], className='col-3'),
                ], className='row pb-4 pt-2 px-5'),
            ], className="bg-light rounded mb-4"),
            dbc.Card([
                html.Div([

                    # Adding one more app/component
                    html.Div([
                        dcc.Graph(id='users-trend', className="shadow")
                    ], className='col-8 pl-5'),
                    # Adding one more app/component
                    html.Div([
                        dcc.Graph(id='relative_users', className="shadow")
                    ], className='col-4 pr-5')
                ], className='row py-4'),
            ], className="bg-light rounded"),

            html.Div(
                [
                    html.Div([
                        html.H3(children='Detailed slide data', className="my-3"),
                        dbc.Button(
                            "Expand",
                            id="button-slide-infos",
                            className="btn btn-secondary my-3 ml-5",
                            n_clicks=0,
                        ),
                    ], className='row py-1 pl-4 d-flex'),
                    dbc.Collapse(
                        dbc.Card([
                            html.Div([

                                # Adding one more app/component
                                html.Div([
                                    dcc.Graph(id='histogram_viewed_slides', className="shadow")
                                ], className='col-8 pl-5'),
                                # Adding one more app/component
                                html.Div([

                                    html.H4(children='Slides with overall least visits'),
                                    html.Ol(id="ul_least_visited_slides"),

                                ], className='col-4 pr-5')

                            ], className='row py-4'),
                            html.Div([

                                # Adding one more app/component
                                html.Div([
                                    dcc.Graph(id='histogram_session_behaviour', className="shadow")
                                ], className='col-8 pl-5'),
                                # Adding one more app/component
                                html.Div([

                                    html.H4(children='Slides with overall most disengages/leaves'),
                                    html.Ol(id="ul_most_disengaging_slides"),

                                ], className='col-4 pr-5')

                            ], className='row py-4'),

                        ], className="bg-light rounded"),
                        id="collapse-slide-infos",
                        is_open=True,
                    ),
                ]),

            html.Div(
                [

                    html.Div([
                        html.H3(children='Detailed quiz data', className="my-3"),
                        dbc.Button(
                            "Expand",
                            id="button-quiz-infos",
                            className="btn btn-secondary my-3 ml-5",
                            n_clicks=0,
                        ),
                    ], className='row py-1 pl-4 d-flex'),
                    dbc.Collapse(
                        dbc.Card([
                            html.Div([
                                # Adding one more app/component
                                html.Div([
                                    dcc.Graph(id='relative_quiz_starters', className="shadow")
                                ], className='col-3 pl-5'),

                                html.Div([
                                    dcc.Graph(id='relative_quiz_completers', className="shadow")
                                ], className='col-3'),
                                # Adding one more app/component
                                html.Div([
                                    dcc.Graph(id='mean_quiz_performance', className="shadow")
                                ], className='col-3'),

                                html.Div([
                                    dcc.Graph(id='quiz_slide_transition', className="shadow")
                                ], className='col-3 pr-5'),

                            ], className='row py-4'),

                        ], className="bg-light rounded"),
                        id="collapse-quiz-infos",
                        is_open=True,
                    ),
                ]),
            html.Div(
                [

                    html.Div([
                        html.H3(children='Detailed shortcut data', className="my-3"),
                        dbc.Button(
                            "Expand",
                            id="button-shortcut-infos",
                            className="btn btn-secondary my-3 ml-5",
                            n_clicks=0,
                        ),
                    ], className='row py-1 pl-4 d-flex'),
                    dbc.Collapse(
                        dbc.Card([
                            html.Div([
                                # Adding one more app/component
                                html.Div([
                                    dcc.Graph(id='relative_shortcut_users', className="shadow")
                                ], className='col-3 pl-5'),

                                html.Div([
                                    dcc.Graph(id='used_shortcuts', className="shadow")
                                ], className='col-3'),
                                # Adding one more app/component

                            ], className='row py-4')
                        ], className="bg-light rounded"),
                        id="collapse-shortcut-infos",
                        is_open=True,
                    ),
                ]),

        ], className='container-fluid')
    ], className='container-fluid py-4')

    return app_layout


"""
    Toggle expandable block
"""
@app.callback(
    Output("collapse-slide-infos", "is_open"),
    Output("button-slide-infos", "children"),
    [Input("button-slide-infos", "n_clicks")],
    [State("collapse-slide-infos", "is_open")],
)
def toggle_collapse_slide_infos(n, is_open):
    if n:
        if is_open:
            text = "Expand"
        else:
            text = "Collapse"
        return not is_open, text
    return is_open, "Collapse"


"""
    Toggle expandable block
"""
@app.callback(
    Output("collapse-quiz-infos", "is_open"),
    Output("button-quiz-infos", "children"),
    [Input("button-quiz-infos", "n_clicks")],
    [State("collapse-quiz-infos", "is_open")],
)
def toggle_collapse_slide_infos(n, is_open):
    if n:
        if is_open:
            text = "Expand"
        else:
            text = "Collapse"
        return not is_open, text
    return is_open, "Collapse"


"""
    Toggle expandable block
"""
@app.callback(
    Output("collapse-shortcut-infos", "is_open"),
    Output("button-shortcut-infos", "children"),
    [Input("button-shortcut-infos", "n_clicks")],
    [State("collapse-shortcut-infos", "is_open")],
)
def toggle_collapse_slide_infos(n, is_open):
    if n:
        if is_open:
            text = "Expand"
        else:
            text = "Collapse"
        return not is_open, text
    return is_open, "Collapse"


"""
    Update cascading dropdown lists when a course is chosen
"""
@app.callback(
    Output('ddl_course', 'options'),
    Input('last_update', 'children')
)
def update_ddl_course_set(last_update_date):
    ddl_course_options = [{'label': "All courses...", 'value': -1}]
    if not df_course.empty:
        ddl_course_options += [{'label': x, 'value': y} for x, y in
                               zip(df_course['name'], df_course['id'])]

    return ddl_course_options


"""
    Update cascading dropdown lists when a course is chosen
"""
@app.callback(
    Output('ddl_slide_set', 'options'),
    Output('ddl_slide_set', 'disabled'),
    Input('ddl_course', 'value'),
    Input('last_update', 'children')
)
def update_ddl_slide_set(course_value, last_update_date):
    options = []
    if not df_slide_set.empty:
        if course_value != -1:
            filtered_df_slide_set = pd.DataFrame.from_records(
                queryset_slide_set.filter(courses__id=course_value).values())
            if not filtered_df_slide_set.empty:
                options = [
                    {'label': x, 'value': y} for x, y in
                    zip(filtered_df_slide_set['name'], filtered_df_slide_set['base_url'])
                ]
            disabled = False
        else:
            options = [
                {'label': x, 'value': y} for x, y in zip(df_slide_set['name'], df_slide_set['base_url'])
            ]
            disabled = True

        if options:
            return [{'label': "All slide sets...", 'value': -1}] + options, disabled

    return [{'label': "All slide sets...", 'value': -1}], False


"""
    Update all plots on ddl change
"""
@app.callback(
    Output('users-trend', 'figure'),
    Output('relative_users', 'figure'),
    Output('ul_least_visited_slides', 'children'),
    Output('ul_most_disengaging_slides', 'children'),
    Output('ddl_slide_set', 'value'),
    Output('histogram_viewed_slides', 'figure'),
    Output('histogram_session_behaviour', 'figure'),
    Output('relative_quiz_starters', 'figure'),
    Output('relative_quiz_completers', 'figure'),
    Output('mean_quiz_performance', 'figure'),
    Output('quiz_slide_transition', 'figure'),
    Output('relative_shortcut_users', 'figure'),
    Output('used_shortcuts', 'figure'),
    Input('ddl_course', 'value'),
    Input('ddl_slide_set', 'value'),
    Input('last_update', 'children')
)
def update_graphs(course_value, slide_set_value, last_update_date):
    if slide_set_value != -1 and course_value == -1:
        slide_set_value = -1
    slide_set_value, course_value, df_sessions_filtered = validate_ddl_and_filter_session(slide_set_value, course_value)

    # if filtered dataset is empty return empty figures
    if len(df_sessions_filtered.index) == 0:
        empty_bar_fig = px.bar(title="No sessions tracked for chosen Slide_Set or Course!")
        empty_pie_fig = px.pie(title="No information for given Slide_Set or Course!")
        empty_list = []
        return empty_bar_fig, empty_pie_fig, empty_list, empty_list, slide_set_value, empty_bar_fig \
            , empty_bar_fig, empty_pie_fig, empty_pie_fig, empty_pie_fig, empty_pie_fig, empty_pie_fig, empty_pie_fig

    # calculate time delta for grouping of sessions
    if len(df_sessions_filtered.index) > 1:
        tdelta = df_sessions_filtered["created_at"].max() - df_sessions_filtered["created_at"].min()
        freq = str(round(tdelta.delta / 30)) + "N"
    else:
        freq = "5min"

    time_group = pd.Grouper(key='created_at', freq=freq, closed='left', label='right')
    first_users = df_sessions_filtered.groupby(["student_id"])['student_id', 'created_at'].min()
    total_users = first_users["student_id"].count()
    students_in_course = df_course[df_course["id"] == course_value]["participants"]
    first_users = first_users.groupby(time_group)["student_id"].nunique()

    df_trend = df_sessions_filtered.groupby(time_group)[
        "session_token", "student_id"].nunique()

    df_trend['first_users'] = first_users

    trend_bar = px.bar(df_trend, barmode="group", y=["session_token", "student_id", "first_users"],
                       color_discrete_sequence=px.colors.qualitative.Set2,
                       title="Trend of activity",
                       labels=dict(created_at="Time", value="Amount", variable="Type of event"))
    trend_bar.update_layout(hovermode="x unified", dragmode='pan')
    legend_labels = {'session_token': 'Sessions', 'student_id': 'Unique users', 'first_users': 'New users'}
    trend_bar.for_each_trace(lambda t: t.update(name=legend_labels[t.name]))

    ul_least_visited_slides = []
    ul_most_disengaging_slides = []
    if not students_in_course.empty and slide_set_value != -1:
        relative_users_pie = create_relative_users_pie(total_users, students_in_course)
        ul_least_visited_slides = create_list_least_visited_slides(df_sessions_filtered)
        ul_most_disengaging_slides = create_list_most_disengaging_slides(df_sessions_filtered)
        histogram_viewed_slides = create_histogram_viewed_slides(df_sessions_filtered, slide_set_value)
        histogram_session_behaviour = create_histogram_session_behaviour(df_sessions_filtered, slide_set_value)
        relative_quiz_starters_pie, relative_quiz_completers_pie, mean_performance_pie, quiz_slide_transition_pie = create_relative_quiz_pies(
            df_sessions_filtered,
            students_in_course)
        relative_shortcut_users, used_shortcuts_pie = create_shortcut_section(df_sessions_filtered, students_in_course)
    else:
        histogram_session_behaviour = px.bar(
            title="No sessions tracked for chosen Slide_Set or Course!")
        histogram_viewed_slides = px.bar(
            title="No sessions tracked for chosen Slide_Set or Course!")
        title_no_data = "Choose a set of slides for <br> detailed information!"
        relative_users_pie = px.pie(title=title_no_data)
        relative_quiz_starters_pie = px.pie(title=title_no_data)
        relative_quiz_completers_pie = px.pie(title=title_no_data)
        mean_performance_pie = px.pie(title=title_no_data)
        quiz_slide_transition_pie = px.pie(title=title_no_data)
        relative_shortcut_users = px.pie(title=title_no_data)
        used_shortcuts_pie = px.pie(title=title_no_data)

    return trend_bar, relative_users_pie, ul_least_visited_slides, ul_most_disengaging_slides, slide_set_value \
        , histogram_viewed_slides, histogram_session_behaviour, relative_quiz_starters_pie, relative_quiz_completers_pie \
        , mean_performance_pie, quiz_slide_transition_pie, relative_shortcut_users, used_shortcuts_pie


"""
    Create plots for shortcut section
"""
def create_shortcut_section(df_sessions_filtered, students_in_course):
    relevant_shortcut_events = df_shortcut_events[
        df_shortcut_events['session_id'].isin(df_sessions_filtered['session_token'])]
    relevant_shortcut_events.rename(columns={'session_id': 'session_token'}, inplace=True)
    relevant_shortcut_events_users = \
        relevant_shortcut_events.merge(df_sessions_filtered, on='session_token', how='left')[
            ['student_id', 'session_token', 'timestamp', 'short_cut']]

    students_using_shortcuts = relevant_shortcut_events_users['student_id'].nunique()

    used_shortcuts = relevant_shortcut_events_users.groupby('short_cut')['short_cut'].count().to_frame()
    used_shortcuts.rename(columns={'short_cut': 'amount'}, inplace=True)

    if students_using_shortcuts >= students_in_course.iloc[0]:
        students_using_shortcuts = students_in_course.iloc[0]
        text_position = 'inside'
    elif students_using_shortcuts == 0:
        text_position = 'inside'
    else:
        text_position = 'auto'

    df_relative_short_users = pd.DataFrame(
        data={'user': ['Using shortcuts', 'Not using shortcuts yet'],
              'count': [students_using_shortcuts, students_in_course.iloc[0] - students_using_shortcuts]})

    relative_shortcut_users_pie = px.pie(df_relative_short_users, title="Users interacting with shortcuts",
                                         values='count',
                                         names='user', hole=.5,
                                         color='user', color_discrete_map={'Using shortcuts': 'green',
                                                                           'Not using shortcuts yet': 'red'},
                                         )

    relative_shortcut_users_pie.update_traces(textposition=text_position, textinfo='percent+value')
    relative_shortcut_users_pie.update_layout(margin=dict(b=80, l=15, r=0), legend=dict(
        yanchor="top",
        y=-0.05,
        xanchor="left",
        x=0.00
    ))
    if used_shortcuts.empty:
        title = "No shortcuts were used/tracked so far"
    else:
        title = "Used shortcuts"
    used_shortcuts_pie = px.pie(used_shortcuts, values='amount', names=used_shortcuts.index, title=title, hole=.5)

    used_shortcuts_pie.update_traces(textinfo='percent+value')
    used_shortcuts_pie.update_layout(margin=dict(b=80, l=15, r=0), legend=dict(
        yanchor="top",
        y=-0.05,
        xanchor="left",
        x=0.00
    ))

    return relative_shortcut_users_pie, used_shortcuts_pie


"""
    Create plots for quiz section
"""
def create_relative_quiz_pies(df_sessions_filtered, students_in_course):
    relevant_quiz_events = df_quiz_events[df_quiz_events['session_id'].isin(df_sessions_filtered['session_token'])]
    relevant_quiz_events.rename(columns={'session_id': 'session_token'}, inplace=True)
    df_quiz_events_users = relevant_quiz_events.merge(df_sessions_filtered, on='session_token', how='left')

    # get quiz starter count (number of users user)
    quiz_events_starters = df_quiz_events_users[df_quiz_events_users['quiz_type'] == 'start']['student_id'].nunique()
    if quiz_events_starters >= students_in_course.iloc[0]:
        quiz_events_starters = students_in_course.iloc[0]
        text_position = 'inside'
    else:
        text_position = 'auto'
    df_relative_starters = pd.DataFrame(
        data={'user': ['User started a quiz at least once', 'User not started a quiz yet'],
              'count': [quiz_events_starters, students_in_course.iloc[0] - quiz_events_starters]})

    quiz_events_total_sessions = df_quiz_events_users['session_token'].nunique()
    relative_starters_pie = px.pie(df_relative_starters, title="Users interacting with quiz",
                                   values='count',
                                   names='user', hole=.5,
                                   color='user', color_discrete_map={'User started a quiz at least once': 'green',
                                                                     'User not started a quiz yet': 'red'},
                                   )

    relative_starters_pie.update_traces(textposition=text_position, textinfo='percent+value')
    relative_starters_pie.update_layout(margin=dict(b=80, l=15, r=0), legend=dict(
        yanchor="top",
        y=-0.05,
        xanchor="left",
        x=0.00
    ))

    if not relevant_quiz_events.empty:
        # get completed session count
        quiz_events_completed = df_quiz_events_users[df_quiz_events_users['quiz_type'] == 'complete'][
            'session_token'].nunique()
        if quiz_events_completed >= quiz_events_total_sessions:
            quiz_events_completed = quiz_events_total_sessions
            text_position = 'inside'
        else:
            text_position = 'auto'
        df_relative_completers = pd.DataFrame(
            data={'user': ['Finished', 'Not finished'],
                  'count': [quiz_events_completed, quiz_events_total_sessions - quiz_events_completed]})

        relative_completers_pie = px.pie(df_relative_completers, title="Started quizzes that were finished",
                                         values='count',
                                         names='user', hole=.5,
                                         color='user', color_discrete_map={'Finished': 'green',
                                                                           'Not finished': 'red'},
                                         )

        relative_completers_pie.update_traces(textposition=text_position, textinfo='percent')
        relative_completers_pie.update_layout(margin=dict(b=80, l=15, r=0), legend=dict(
            yanchor="top",
            y=-0.05,
            xanchor="left",
            x=0.00
        ))

        # get mean quiz performance
        quiz_mean_performance = df_quiz_events_users[df_quiz_events_users['quiz_type'] == 'complete'][
            'percentage'].mean()

        df_relative_completers = pd.DataFrame(
            data={'user': ['Finished', 'Not finished'],
                  'count': [quiz_mean_performance, 100 - quiz_mean_performance]})

        mean_performance_pie = px.pie(df_relative_completers, title="Mean quiz performance", values='count',
                                      names='user', hole=.5,
                                      color='user', color_discrete_map={'Finished': 'green',
                                                                        'Not finished': 'red'},
                                      )

        mean_performance_pie.update_traces(textinfo='percent')
        mean_performance_pie.update_layout(margin=dict(b=80, l=15, r=0))
        mean_performance_pie.update(layout_showlegend=False)

        # get percentage of sessions having slide transitions between quiz start and complete
        # quiz_with_slideTransitions = df_quiz_events_users[df_quiz_events_users['quiz_type'] == 'complete'][
        #    'percentage'].mean()
        relevant_quiz_events = df_quiz_events[df_quiz_events['session_id'].isin(df_sessions_filtered['session_token'])]

        quiz_stop_events = relevant_quiz_events[relevant_quiz_events['quiz_type'] == "complete"].rename(
            columns={'timestamp': 'completed_at'})
        quiz_start_events = relevant_quiz_events[relevant_quiz_events['quiz_type'] == "start"].rename(
            columns={'timestamp': 'started_at'})

        quiz_stop_events = quiz_stop_events[['completed_at', 'session_id']]
        quiz_stop_events['started_at'] = quiz_stop_events.apply(lambda x: get_quiz_started_time(x, quiz_start_events),
                                                                axis=1)

        relevant_slide_transition_events = df_slide_transition_events[
            df_slide_transition_events['session_id'].isin(quiz_stop_events['session_id'])][['session_id', 'timestamp']]

        slide_transitons = quiz_stop_events.apply(
            lambda x: get_quiz_slide_transitions(x, relevant_slide_transition_events), axis=1)

        total_quizzes = slide_transitons.count()

        mean_slide_transitions = slide_transitons.mean()

        quizzes_with_transitions = slide_transitons.loc[lambda x: x > 0].count()

        if quizzes_with_transitions == 0 or total_quizzes == quizzes_with_transitions:
            text_position = 'inside'
        else:
            text_position = 'auto'

        df_relative_slide_transitions = pd.DataFrame(
            data={'user': ['Quiz completed without slide transitions',
                           'Slide transition within quiz'],
                  'count': [total_quizzes - quizzes_with_transitions, quizzes_with_transitions]})

        quiz_slide_transition_pie = px.pie(df_relative_slide_transitions, title="Quizzes with slide transitions <br>"
                                                                                "(Mean slide transitions per quiz: "
                                                                                + str(
            "{:.2f}".format(mean_slide_transitions)) + ")",
                                           values='count',
                                           names='user', hole=.5,
                                           color='user',
                                           color_discrete_map={'Quiz completed without slide transitions': 'green',
                                                               'Slide transition within quiz': 'red'},
                                           )

        quiz_slide_transition_pie.update_traces(textposition=text_position, textinfo='percent+value')
        quiz_slide_transition_pie.update_layout(margin=dict(b=80, l=15, r=0), legend=dict(
            yanchor="top",
            y=-0.05,
            xanchor="left",
            x=0.00
        ))
    else:
        relative_completers_pie = px.pie(title="No quiz information tracked so yset!")
        mean_performance_pie = px.pie(title="No quiz information tracked so yet!")
        quiz_slide_transition_pie = px.pie(title="NNo quiz information tracked so yet!")

    return relative_starters_pie, relative_completers_pie, mean_performance_pie, quiz_slide_transition_pie


"""
    Quiz plot helper function to filter each row
"""
def get_quiz_started_time(row, start_events):
    start_date = start_events.query('(session_id == @row["session_id"]) & (started_at < @row["completed_at"])')[
        "started_at"].max()
    return start_date


"""
    Quiz plot helper function to filter each row
"""
def get_quiz_slide_transitions(row, slide_transition_events):
    slide_transitions = slide_transition_events.query('(session_id == @row["session_id"]) & (timestamp < @row['
                                                      '"completed_at"]) & (timestamp > @row["started_at"])')[
        'timestamp'].count()
    return slide_transitions


"""
    Create histogram users
"""
def create_histogram_viewed_slides(df_sessions_filtered, slide_set_value):
    relevant_events = df_event[df_event['session_id'].isin(df_sessions_filtered['session_token'])]
    relevant_events.rename(columns={'session_id': 'session_token'}, inplace=True)
    relevant_events = relevant_events.merge(df_sessions_filtered, on='session_token', how='left')
    relevant_events = relevant_events[["absolute_url", 'student_id', 'total_slides']]
    relevant_events = relevant_events.groupby(["student_id"]).agg({'absolute_url': 'nunique', 'total_slides': 'first'})
    relevant_events['slide_percent'] = relevant_events.eval('absolute_url / total_slides  * 100')
    relevant_events['binned'] = pd.cut(relevant_events['slide_percent'], bins=list(range(0, 101, 10)))
    relevant_events = relevant_events.groupby('binned').size()

    relevant_events = pd.DataFrame(
        {'percent_range': relevant_events.index.astype(str), 'count': relevant_events.values})

    histogram_bar = px.bar(relevant_events, x="percent_range",
                           y="count",
                           title="How many students viewed how many slides in slide set: " + slide_set_value,
                           labels={
                               "percent_range": "% of slides viewed at least once",
                               "count": "Students"
                           })

    histogram_bar.update_layout(hovermode="x unified", dragmode='pan')

    return histogram_bar


"""
    Create histogram sessions
"""
def create_histogram_session_behaviour(df_sessions_filtered, slide_set_value):
    relevant_events = df_event[df_event['session_id'].isin(df_sessions_filtered['session_token'])]
    relevant_events.rename(columns={'session_id': 'session_token'}, inplace=True)
    relevant_events = relevant_events.merge(df_sessions_filtered, on='session_token', how='left')
    relevant_events = relevant_events[["absolute_url", 'session_token', 'total_slides']]
    relevant_events = relevant_events.groupby(["session_token"]).agg(
        {'absolute_url': 'nunique', 'total_slides': 'first'})
    relevant_events['slide_percent'] = relevant_events.eval('absolute_url / total_slides  * 100')
    relevant_events['binned'] = pd.cut(relevant_events['slide_percent'], bins=list(range(0, 101, 10)))
    relevant_events = relevant_events.groupby('binned').size()
    relevant_events = pd.DataFrame(
        {'percent_range': relevant_events.index.astype(str), 'count': relevant_events.values})

    histogram_bar = px.bar(relevant_events, x="percent_range",
                           y="count",
                           title="How many slides were viewed per session: " + slide_set_value,
                           labels={
                               "percent_range": "% of slides viewed in session",
                               "count": "Sessions"
                           })
    histogram_bar.update_layout(hovermode="x unified", dragmode='pan')

    return histogram_bar


"""
    create list for least visited slides
"""
def create_list_least_visited_slides(df_sessions_filtered):
    events = df_dwell_time[df_dwell_time["session_id"].isin(df_sessions_filtered["session_token"])]
    events = events.groupby(["absolute_url"])["absolute_url"].count()
    events = events.sort_values()
    options = []
    for i, v in events.items():
        if len(options) < 10:
            options.append(html.Li(i + " (" + str(v) + " visits)"))
        else:
            break
    return options


"""
    create list with slides having the most disengages
"""
def create_list_most_disengaging_slides(df_sessions_filtered):
    events = df_event[df_event["session_id"].isin(df_sessions_filtered["session_token"])]
    last_events = events.loc[events.groupby(['session_id'], sort=False)['timestamp'].idxmax()][
        ['id', 'session_id', 'absolute_url', 'timestamp']]
    last_events_on_slide = last_events.groupby(["absolute_url"])["absolute_url"].count()
    last_events_on_slide = last_events_on_slide.sort_values(ascending=False)
    options = []
    for i, v in last_events_on_slide.items():
        if len(options) < 10:
            options.append(html.Li(i + " (" + str(v) + " left on this slide)"))
        else:
            break
    return options


"""
    create pie chart for relative users per slide_set
"""
def create_relative_users_pie(total_users, students_in_course):
    if total_users >= students_in_course.iloc[0]:
        total_users = students_in_course.iloc[0]
        text_position = 'inside'
    else:
        text_position = 'auto'
    df_relative_users = pd.DataFrame(
        data={'user': ['Accessed set of slides at least once', 'Not accessed set of slides yet'],
              'count': [total_users, students_in_course.iloc[0] - total_users]})

    relative_users_pie = px.pie(df_relative_users, title="Users accessing set of slides:", values='count',
                                names='user', hole=.5,
                                color='user', color_discrete_map={'Accessed set of slides at least once': 'green',
                                                                  'Not accessed set of slides yet': 'red'},
                                )
    relative_users_pie.update_traces(textposition=text_position, textinfo='percent+value')
    relative_users_pie.update_layout(margin=dict(b=80, l=15, r=0), legend=dict(
        yanchor="top",
        y=-0.05,
        xanchor="left",
        x=0.00
    ))
    return relative_users_pie


"""
    validate ddl input and prefilter dataframes
"""
def validate_ddl_and_filter_session(slide_set_value, course_value):
    if slide_set_value != -1 and course_value != -1:
        if not queryset_slide_set.filter(pk=slide_set_value, courses__id=course_value).exists():
            slide_set_value = -1

    df_sessions_filtered = df_sessions
    if course_value != -1:
        time_period_id = df_course[df_course['id'] == course_value]['time_period_id'].iloc[0]
        time_period = df_TimePeriod[df_TimePeriod['id'] == time_period_id]

        # are used in df_query
        start_date = pd.Timestamp(
            timezone.make_aware(datetime.combine(time_period['start_date'].iloc[0], time(0, 0, 0))))
        end_date = pd.Timestamp(
            timezone.make_aware(datetime.combine(time_period['end_date'].iloc[0], time(23, 59, 59))))

    # filter dataset according to dropdown lists
    if slide_set_value != -1:
        df_sessions_filtered = df_sessions.query(
            'slide_set_id == @slide_set_value & created_at > '
            '@start_date & created_at < @end_date')

    elif course_value != -1:

        filtered_df_slide_set = pd.DataFrame.from_records(queryset_slide_set.filter(courses__id=course_value).values())
        if not filtered_df_slide_set.empty:
            filtered_df_slide_set_base_url = filtered_df_slide_set['base_url']
            df_sessions_filtered = df_sessions.query(
                'slide_set_id in @filtered_df_slide_set_base_url & created_at > '
                '@start_date & created_at < @end_date')
        else:
            df_sessions_filtered = pd.DataFrame()
    return slide_set_value, course_value, df_sessions_filtered


if all_tables:
    app.layout = serve_layout()

if __name__ == '__main__':
    app.run_server(8052, debug=False)
