import { useState } from 'react';
import { EntityFormWrapper } from './shared/FormWrapper';
import styles from './Form.module.css';

interface Props {
    close(): void;
    setActive: (name: string | null) => void;
}

const minWeight = 0;
const maxWeight = 5;

interface PriorityField {
    key: string;
    label: string;
    state: number;
    setState: (val: number) => void;
    default: number;
    reset: () => void;
}

export default function SettingsForm({ close, setActive }: Props) {
    const [keepIdealTeamSize, setKeepIdealTeamSize] = useState(3);
    const [maximizeCourtUsage, setMaximizeCourtUsage] = useState(2);
    const [balanceLvl, setBalanceLvl] = useState(4);
    const [reduceLvlGaps, setReduceLvlGaps] = useState(1);
    const [diversifyPartners, setDiversifyPartners] = useState(3);
    const [diversifyOpponents, setDiversifyOpponents] = useState(2);

    const fields: PriorityField[] = [
        {
            key: 'keepIdealTeamSize',
            label: 'Keep ideal team size',
            state: keepIdealTeamSize,
            setState: setKeepIdealTeamSize,
            default: 3,
            reset: () => setKeepIdealTeamSize(3),
        },
        {
            key: 'maximizeCourtUsage',
            label: 'Maximize court usage',
            state: maximizeCourtUsage,
            setState: setMaximizeCourtUsage,
            default: 2,
            reset: () => setMaximizeCourtUsage(2),
        },
        {
            key: 'balanceLvl',
            label: 'Balance levels',
            state: balanceLvl,
            setState: setBalanceLvl,
            default: 4,
            reset: () => setBalanceLvl(4),
        },
        {
            key: 'reduceLvlGaps',
            label: 'Reduce level gaps',
            state: reduceLvlGaps,
            setState: setReduceLvlGaps,
            default: 1,
            reset: () => setReduceLvlGaps(1),
        },
        {
            key: 'diversifyPartners',
            label: 'Diversify partners',
            state: diversifyPartners,
            setState: setDiversifyPartners,
            default: 3,
            reset: () => setDiversifyPartners(3),
        },
        {
            key: 'diversifyOpponents',
            label: 'Diversify opponents',
            state: diversifyOpponents,
            setState: setDiversifyOpponents,
            default: 2,
            reset: () => setDiversifyOpponents(2),
        },
    ];

    const displayWeight = (weight: number) => {
        if (weight === 0) {
            return (
                <span>
                    <span>: </span>
                    <span className={styles.disabledInput}>disabled</span>
                </span>
            );
        }
        return (
            <span>
                <span>: </span>
                <span>{weight}</span>
            </span>
        );
    };

    const handleSubmit = () => {
        // TODO: (later)
    };

    return (
        <div>
            {fields.map((f) => (
                <div key={f.key}>
                    <p className={styles.title}>
                        {f.label}
                        {displayWeight(f.state)}
                    </p>
                    <EntityFormWrapper
                        onSubmit={() => { }}
                        onCancel={f.reset}
                        isSubmitting={false} // todo: (later) replace with actual loading state if needed
                    >
                        <input
                            className="slider"
                            type="range"
                            min={minWeight}
                            max={maxWeight}
                            step={1}
                            value={f.state}
                            onChange={(e) => f.setState(Number(e.target.value))}
                        />
                    </EntityFormWrapper>
                </div>
            ))}

            <button
                type="button"
                className={`button primary ${styles.submitButton}`}
                onClick={handleSubmit}
            >
                save priorities
            </button>
        </div>
    );
}