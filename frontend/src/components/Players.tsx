import { useEffect, useState } from "react";

const Players = () => {
    const [players, setPlayers] = useState<string[]>([]);

    useEffect(() => {
        // fetch("/api/player/list")
        // .then(res => res.json())
        // .then(data => {
        //     const allPlayers = [
        //     ...(data.active_players?.split("\n") || []),
        //     ...(data.resting_players?.split("\n") || []),
        //     ];
        //     setPlayers(allPlayers);
        // });
    }, []);

    return (
        <div className="p-4">
        <h2 className="text-2xl font-bold mb-4">Players</h2>
        <ul className="list-disc pl-5">
            {players.map((p, i) => <li key={i}>{p}</li>)}
        </ul>
        </div>
    );
}

export default Players;
