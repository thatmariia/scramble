import { EntityFormWrapper } from './shared/FormWrapper';
import { CustomSelect } from '../../elements/CustomSelect';
import { useLoadSession, useSessionNames } from '../../hooks/session';
import { useSessionName } from '../../context/SessionContext';
import styles from './Form.module.css'; 
import { toast } from 'sonner';

interface Props {
    close(): void;
    setActive: (name: string | null) => void;
}

export default function LoadSessionForm({ close, setActive }: Props) {
    const loadSession = useLoadSession();
    const { data: sessionNames = [], isLoading } = useSessionNames();
    const { name, setName } = useSessionName();

    const options = sessionNames.map((n) => ({
        label: n,
        value: n,
    }));

    return (
        <div>
            <p className={styles.title}>
                Load a session
            </p>
            <CustomSelect
                value={name && sessionNames.includes(name) ? name : ''}
                options={options}
                onChange={(val) => {
                    console.log('Selected session:', val);
                    setName(val);

                    const trimmed = val.trim();
                    if (!trimmed) {
                        toast.error('Please enter a session name');
                        return;
                    }

                    loadSession.mutate(
                        { name: trimmed },
                        {
                            onSuccess: () => {
                                toast.success(`Loaded session "${trimmed}"`);
                                setActive(trimmed);
                                close();
                            },
                            onError: (err) => {
                                toast.error(`Could not load session "${trimmed}"`);
                                console.error(err);
                            },
                        }
                    );
                }}
            />
        </div>
    );
}