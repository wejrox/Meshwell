#
# Database queries to get the details required for the creation of discord channels.
# Queries must be executed via database connection cursor execution.
# 

# Amount of time in between each query to the database in seconds.
query_interval = 300 

# Get any sessions that haven't happened yet but will happen in the next 10 minutes.
# result[0] = session_id
# result[1] = discord_id
upcoming_sessions_query = (
    "SELECT api_session.id as session_id, api_profile.discord_id"
    " FROM api_session, api_profile, api_session_profile"
    " WHERE api_session_profile.session_id = api_session.id"
    " AND api_session_profile.profile_id = api_profile.id"
    " AND api_session.start IS NOT NULL"
    " AND api_session.end_time IS NOT NULL"
    " AND api_session.start <= NOW() + INTERVAL "+str(query_interval)+" SECOND"
    " AND api_session.start > NOW();"
)

# Get any sessions that ended since the last interval.
# result[0] = session_id
# result[1] = discord_id
# result[3] = session_profile_id (session with the meshwell profile attached)
past_sessions_query = (
    "SELECT api_session.id as session_id, api_profile.discord_id, api_session_profile.id"
    " FROM api_session, api_profile, api_session_profile"
    " WHERE api_session_profile.session_id = api_session.id"
    " AND api_session_profile.profile_id = api_profile.id"
    " AND api_session.start IS NOT NULL"
    " AND api_session.start < NOW()"
    " AND api_session.end_time IS NOT NULL"
    " AND api_session.end_time <= NOW() + INTERVAL "+str(query_interval)+" SECOND"
    " AND api_session.end_time >= NOW() - INTERVAL "+str(query_interval)+" SECOND;"
)
