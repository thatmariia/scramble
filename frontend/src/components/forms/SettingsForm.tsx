import { useState } from 'react';
import { EntityFormWrapper } from './shared/FormWrapper';
import styles from './Form.module.css';

interface Props {
    close(): void;
    setActive: (name: string | null) => void;
}

export default function SettingsForm({ close, setActive }: Props) {
    const [minTeamSize, setMinTeamSize] = useState('');
    const initMinTeamSize = minTeamSize || '2';
    const [maxTeamSize, setMaxTeamSize] = useState('');
    const initMaxTeamSize = maxTeamSize || '4';
    const [nrTeams, setNrTeams] = useState('');
    const initNrTeams = nrTeams || '2';

    const doNothing = () => {};

    const handleCancelMinTeamSize = () => {
        setMinTeamSize(initMinTeamSize);
    };
    const handleCancelMaxTeamSize = () => {
        setMaxTeamSize(initMaxTeamSize);
    };
    const handleCancelNrTeams = () => {
        setNrTeams(initNrTeams);
    };

    const handleSubmit = () => {
        // todo: (later)
    };

    return (
        <div>
            <p className={styles.title}>
                Min (ideal) team size{ minTeamSize ? `: ${minTeamSize}` : ""}
            </p>
            <EntityFormWrapper
                onSubmit={doNothing}
                onCancel={handleCancelMinTeamSize}
                isSubmitting={false} // todo: (later) replace with actual loading state if needed
            >
                <input
                    className="slider"
                    type="range"
                    min={1}
                    max={10}
                    step={1}
                    value={minTeamSize}
                    onChange={(e) => setMinTeamSize(e.target.value)}
                />
            </EntityFormWrapper>

            <p className={styles.title}>
                Max team size{maxTeamSize ? `: ${maxTeamSize}` : ""}
            </p>
            <EntityFormWrapper
                onSubmit={doNothing}
                onCancel={handleCancelMaxTeamSize}
                isSubmitting={false} // todo: (later) replace with actual loading state if needed
            >
                <input
                    className="slider"
                    type="range"
                    min={1}
                    max={10}
                    step={1}
                    value={maxTeamSize}
                    onChange={(e) => setMaxTeamSize(e.target.value)}
                />
            </EntityFormWrapper>

            <p className={styles.title}>
                Min teams per court{ nrTeams ? `: ${nrTeams}` : ""}
            </p>
            <EntityFormWrapper
                onSubmit={doNothing}
                onCancel={handleCancelNrTeams}
                isSubmitting={false} // todo: (later) replace with actual loading state if needed
            >
                <input
                    className="slider"
                    type="range"
                    min={1}
                    max={10}
                    step={1}
                    value={nrTeams}
                    onChange={(e) => setNrTeams(e.target.value)}
                />
            </EntityFormWrapper>

            <button
                type="button"
                className={`button primary ${styles.submitButton}`}
                onClick={handleSubmit}
            >
                save settings
            </button>
        </div>
    );
}