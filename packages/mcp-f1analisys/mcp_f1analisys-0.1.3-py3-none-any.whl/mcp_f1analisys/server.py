import httpx
from pydantic import Field
from mcp.server.fastmcp import FastMCP, Image

mcp = FastMCP(
    "mcp-f1analisys",
    timeout=30.0
)

client = httpx.AsyncClient(
    base_url="https://f1analisys-production.up.railway.app/api",
    timeout=httpx.Timeout(30.0, connect=10.0),
    limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
    follow_redirects=True
)

def get_drivers_laps_path(drivers_laps_range:dict) -> str:
    drivers_path = "compare"
    keys_list = list(drivers_laps_range.keys())
    for driver in keys_list:
        lap_range = drivers_laps_range[driver]
        drivers_path += f"/{driver}"
        for lap in lap_range:
            drivers_path += f"/{lap}"
        if keys_list.index(driver) < len(keys_list) - 1:
            drivers_path += "/vs"
    return drivers_path

def get_full_path(params:list) -> str:
    full_path = ""
    for param in params:
        if isinstance(param, dict): 
            param = get_drivers_laps_path(param)
        full_path += "/"+param if isinstance(param, str) else "/"+str(param)
    return full_path

async def get_image_analisys(params:list) -> Image:
    full_path = get_full_path(params)
    response = await client.get(full_path)
    response.raise_for_status()
    return Image(data=response.content, format="png")

@mcp.tool(name="top_speed")
async def get_top_speed(
    type_session: str = Field(description="Type of session in general terms: official or pretest (pre-session test)"),
    year: int = Field(description="The year of the season when the session was held"),
    round: int = Field(description="The round number of the championship, for example 1 for the first Grand Prix."),
    session: str = Field(description="The exact name of the session within the event, such as 'FP1', 'FP2', 'Q', 'R', or 'Sprint'.")
    ) -> Image:
    """Get F1 top speed data visualization from the session"""

    result = await get_image_analisys([type_session,"top_speed",year,round,session])
    return result

@mcp.tool(name="braking")
async def get_braking(
    type_session: str = Field(description="Type of session in general terms: official or pretest (pre-session test)"),
    year: int = Field(description="The year of the season when the session was held"),
    round: int = Field(description="The round number of the championship, for example 1 for the first Grand Prix."),
    session: str = Field(description="The exact name of the session within the event, such as 'FP1', 'FP2', 'Q', 'R', or 'Sprint'.")
    ) -> Image:
    """Get F1 average braking data visualization from the session"""

    result = await get_image_analisys([type_session,"braking",year,round,session])
    return result

@mcp.tool(name="throttle")
async def get_throttle(
    type_session: str = Field(description="Type of session in general terms: official or pretest (pre-session test)"),
    year: int = Field(description="The year of the season when the session was held"),
    round: int = Field(description="The round number of the championship, for example 1 for the first Grand Prix."),
    session: str = Field(description="The exact name of the session within the event, such as 'FP1', 'FP2', 'Q', 'R', or 'Sprint'.")
    ) -> Image:
    """Get F1 average throttle data visualization from the session"""

    result = await get_image_analisys([type_session,"throttle",year,round,session])
    return result

@mcp.tool(name="fastest_laps")
async def get_fastest_laps(
    type_session: str = Field(description="Type of session in general terms: official or pretest (pre-session test)"),
    year: int = Field(description="The year of the season when the session was held"),
    round: int = Field(description="The round number of the championship, for example 1 for the first Grand Prix."),
    session: str = Field(description="The exact name of the session within the event, such as 'FP1', 'FP2', 'Q', 'R', or 'Sprint'.")
    ) -> Image:
    """Get F1 fastest laps data visualization from the session"""

    result = await get_image_analisys([type_session,"fastest_laps",year,round,session])
    return result

@mcp.tool(name="lap_time_average")
async def get_lap_time_average(
    type_session: str = Field(description="Type of session in general terms: official or pretest (pre-session test)"),
    year: int = Field(description="The year of the season when the session was held"),
    round: int = Field(description="The round number of the championship, for example 1 for the first Grand Prix."),
    session: str = Field(description="The exact name of the session within the event, such as 'FP1', 'FP2', 'Q', 'R', or 'Sprint'.")
    ) -> Image:
    """Get F1 lap time average data visualization from the session"""

    result = await get_image_analisys([type_session,"lap_time_average",year,round,session])
    return result

@mcp.tool(name="team_performace")
async def get_team_performace(
    type_session: str = Field(description="Type of session in general terms: official or pretest (pre-session test)"),
    year: int = Field(description="The year of the season when the session was held"),
    round: int = Field(description="The round number of the championship, for example 1 for the first Grand Prix."),
    session: str = Field(description="The exact name of the session within the event, such as 'FP1', 'FP2', 'Q', 'R', or 'Sprint'.")
    ) -> Image:
    """Get F1 team performance data visualization from the session"""

    result = await get_image_analisys([type_session,"team_performace",year,round,session])
    return result

@mcp.tool(name="race_position_evolution")
async def get_race_position_evolution(
    type_session: str = Field(description="Type of session in general terms: official or pretest (pre-session test)"),
    year: int = Field(description="The year of the season when the session was held"),
    round: int = Field(description="The round number of the championship, for example 1 for the first Grand Prix."),
    session: str = Field(description="The exact name of the session within the event, such as 'FP1', 'FP2', 'Q', 'R', or 'Sprint'. In this case, this image can only take 'R' and 'Q' as session.")
    ) -> Image:
    """Get F1 race position evolution data visualization from the session"""

    result = await get_image_analisys([type_session,"race_position_evolution",year,round,session])
    return result

@mcp.tool(name="lap_time_distribution")
async def get_lap_time_distribution(
    type_session: str = Field(description="Type of session in general terms: official or pretest (pre-session test). In this only this image can only take 'official' as type_session"),
    year: int = Field(description="The year of the season when the session was held"),
    round: int = Field(description="The round number of the championship, for example 1 for the first Grand Prix."),
    session: str = Field(description="The exact name of the session within the event, such as 'FP1', 'FP2', 'Q', 'R', or 'Sprint'. In this case, this image can only take 'R' and 'Q' as session.")
    ) -> Image:
    """Get F1 lap time distribution data visualization from the session"""

    result = await get_image_analisys([type_session,"lap_time_distribution",year,round,session])
    return result

@mcp.tool(name="fastest_drivers_compound")
async def get_fastest_drivers_compound(
    type_session: str = Field(description="Type of session in general terms: official or pretest (pre-session test)"),
    year: int = Field(description="The year of the season when the session was held"),
    round: int = Field(description="The round number of the championship, for example 1 for the first Grand Prix."),
    session: str = Field(description="The exact name of the session within the event, such as 'FP1', 'FP2', 'Q', 'R', or 'Sprint'.")
    ) -> Image:
    """Get F1 fatest drivers compound data visualization from the session"""

    result = await get_image_analisys([type_session,"fastest_drivers_compound",year,round,session])
    return result

@mcp.tool(name="long_runs")
async def get_long_runs(
    type_session: str = Field(description="Type of session in general terms: official or pretest (pre-session test)"),
    year: int = Field(description="The year of the season when the session was held"),
    round: int = Field(description="The round number of the championship, for example 1 for the first Grand Prix."),
    session: str = Field(description="The exact name of the session within the event, such as 'FP1', 'FP2', 'Q', 'R', or 'Sprint'."),
    drivers_laps_range: dict = Field(
        description="""Dictionary list where the key is the name of the driver and value is driver range laps selected
                    E.G:{ 
                            LEC: [8,15],
                            VER: [9,12],
                            PIA: [10,14]
                        }"""
    ),
    ) -> Image:
    """Get a long run analysis of specific drivers between selected laps of the session"""

    result = await get_image_analisys([type_session,"long_runs",year,round,session, drivers_laps_range])
    return result

@mcp.tool(name="track_dominance")
async def get_track_dominance(
    type_session: str = Field(description="Type of session in general terms: official or pretest (pre-session test)"),
    year: int = Field(description="The year of the season when the session was held"),
    round: int = Field(description="The round number of the championship, for example 1 for the first Grand Prix."),
    session: str = Field(description="The exact name of the session within the event, such as 'FP1', 'FP2', 'Q', 'R', or 'Sprint'."),
    drivers_laps_range: dict = Field(
        description="""Dictionary list where the key is the name of the driver and value is the lap selected
                    E.G:{ 
                            LEC: [8],
                            VER: [9],
                            PIA: [10]
                        }"""
        )
    ) -> Image:
    """Get F1 track dominance data visualization from the session"""

    result = await get_image_analisys([type_session,"track_dominance",year,round,session,drivers_laps_range])
    return result

@mcp.tool(name="comparative_lap_time")
async def get_comparative_lap_time(
    type_session: str = Field(description="Type of session in general terms: official or pretest (pre-session test)"),
    year: int = Field(description="The year of the season when the session was held"),
    round: int = Field(description="The round number of the championship, for example 1 for the first Grand Prix."),
    session: str = Field(description="The exact name of the session within the event, such as 'FP1', 'FP2', 'Q', 'R', or 'Sprint'."),
    drivers_laps_range: dict = Field(
        description="""Dictionary list where the key is the name of the driver and value is the lap selected
                    E.G:{ 
                            LEC: [8],
                            VER: [9],
                            PIA: [10]
                        }"""
        )
    ) -> Image:
    """Get F1 comparative lap time data visualization from the session"""

    result = await get_image_analisys([type_session,"comparative_lap_time",year,round,session,drivers_laps_range])
    return result

def main():
    mcp.run()