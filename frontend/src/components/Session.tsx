import { AddEntityButton } from './shared/AddEntityButton';
import { useSessionName } from '../context/SessionContext';
import { useSession } from '../hooks/session';
import NewSessionForm from './forms/NewSessionForm';
import LoadSessionForm from './forms/LoadSessionForm';

export default function Session() {
    const { name: active, setName } = useSessionName();
    const { isLoading } = useSession(active);


    if (isLoading) return <p className="p-4">Loading session…</p>;

    return (
        <div className="p-4 space-y-4">
            <h3 className="text-3xl font-bold">Session</h3>

            <p className="text-lg">
                <strong>Current:</strong> {active ?? 'No active session'}
            </p>

            <AddEntityButton
                buttonLabel="+ Start new session"
                color="blue"
                renderForm={(close) => (
                    <NewSessionForm close={close} setActive={setName} />
                )}
            />

            <AddEntityButton
                buttonLabel="Load session"
                color="emerald"
                renderForm={(close) => (
                    <LoadSessionForm close={close} setActive={setName} />
                )}
            />
        </div>
    );
}