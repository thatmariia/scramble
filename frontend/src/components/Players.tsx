// import { useEffect, useState } from "react";
import { usePlayers } from '../hooks/player';
import { ApiError } from '../api';


const Players = () => {
    const { data, isLoading, error } = usePlayers();

    const everyone = [
        ...(data?.active  ?? []),
        ...(data?.resting ?? []),
    ];

    return (
        <div className="p-4">
        <h1 className="text-3xl font-bold mb-4">Players</h1>
        <ul className="list-disc pl-5">
            {everyone.map((p) => (
            <li key={p.id}>{p.name} (lvl {p.level})</li>
            ))}
        </ul>
        </div>
    );
}

export default Players;
