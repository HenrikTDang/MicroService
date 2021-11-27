import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
        
        fetch(`http://microservice-annson.eastus.cloudapp.azure.com:8100/stats`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Stats")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getStats]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
                <h1>Latest Stats</h1>
                <table className={"StatsTable"}>
					<tbody>
						<tr>
							<th>Personal Information</th>
							<th>Membership Validity</th>
						</tr>
						<tr>
							<td># Personal Information    : {stats['num_personal_info_readings']}</td>
							<td># Membership Validity: {stats['num_membership_validate_readings']}</td>
						</tr>
                        <tr>
							<td colspan="2">Max Age: {stats['max_personal_info_readings']}</td>
						</tr>
						<tr>
							<td colspan="2">Max Membership Duration (In months): {stats['max_membership_validate_readings']}</td>
						</tr>
					</tbody>
                </table>
                <h3>Last Updated: {stats['last_updated']}</h3>

            </div>  
        )
    }
}
