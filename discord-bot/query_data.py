query_interval = 300 # Amount of time in between each query to the database

# Get any sessions that haven't happened yet but will happen in the next 10 minutes
upcoming_sessions_query = (
    "SELECT api_session.id as session_id, api_profile.discord_name"
    " FROM api_session, api_profile, api_session_profile"
    " WHERE api_session_profile.session_id = api_session.id"
    " AND api_session_profile.profile_id = api_profile.id"
    " AND api_session.start IS NOT NULL"
    " AND api_session.end_time IS NOT NULL"
    " AND api_session.start <= NOW() + INTERVAL "+str(query_interval)+" SECOND"
    " AND api_session.start > NOW();"
    )

# Get any sessions that ended since the last interval
past_sessions_query = (
    "SELECT api_session.id as session_id, api_profile.discord_name, api_session_profile.id"
    " FROM api_session, api_profile, api_session_profile"
    " WHERE api_session_profile.session_id = api_session.id"
    " AND api_session_profile.profile_id = api_profile.id"
    " AND api_session.start IS NOT NULL"
    " AND api_session.start < NOW()"
    " AND api_session.end_time IS NOT NULL"
    " AND api_session.end_time <= NOW() + INTERVAL "+str(query_interval)+" SECOND"
    " AND api_session.end_time >= NOW() - INTERVAL "+str(query_interval)+" SECOND;"
)