import { useState, useEffect } from 'react';
import { EntityFormWrapper } from './shared/FormWrapper';
import styles from './Form.module.css';

interface Props {
    close(): void;
    setActive: (name: string | null) => void;
}

export default function SettingsForm({ close, setActive }: Props) {
    const [minTeamSize, setMinTeamSize] = useState(2);
    const initMinTeamSize = minTeamSize || 2;
    const [maxTeamSize, setMaxTeamSize] = useState(2);
    const initMaxTeamSize = maxTeamSize || 2;
    const [nrTeams, setNrTeams] = useState(2);
    const initNrTeams = nrTeams || 2;

    const doNothing = () => {};

    useEffect(() => {
        if (minTeamSize > maxTeamSize) {
            setMaxTeamSize(minTeamSize);
        }
    }, [minTeamSize]);

    useEffect(() => {
        if (maxTeamSize < minTeamSize) {
            setMinTeamSize(maxTeamSize);
        }
    }, [maxTeamSize]);

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
                    onChange={(e) => setMinTeamSize(Number(e.target.value))}
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
                    onChange={(e) => setMaxTeamSize(Number(e.target.value))}
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
                    onChange={(e) => setNrTeams(Number(e.target.value))}
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