import Session from "../components/Session";
import Players from "../components/Players";
import Courts from "../components/Courts";


export default function Scramble() {
    return (
        <div>
        <h1>Scramble</h1>
        <Session />
        <Players />
        <Courts />
        </div>
    );
}