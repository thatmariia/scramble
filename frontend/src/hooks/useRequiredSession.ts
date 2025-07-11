import { useSessionName } from '../context/SessionContext';

export function useRequiredSessionName() {
    const { name } = useSessionName();
    if (!name) throw new Error('No active session selected');
    return name;
}