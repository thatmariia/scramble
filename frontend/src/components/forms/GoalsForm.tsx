import { useState, useRef } from 'react';
import { EntityFormWrapper } from './shared/FormWrapper';
import HoverTooltip from '../../elements/HoverTooltip';
import styles from './Form.module.css';
import { Info } from 'lucide-react';

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
    description?: string;
    setState: (val: number) => void;
    default: number;
    reset: () => void;
}

function TooltipIcon({ id, description }: { id: string; description: string }) {
    const ref = useRef<HTMLSpanElement>(null);

    return (
        <span className={styles.tooltipIcon} ref={ref}>
            <Info className="icon" />
            <HoverTooltip triggerRef={ref}>
                <span id={id} className={styles.tooltipContent}>
                    {description}
                </span>
            </HoverTooltip>
        </span>
    );
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
            description: "Prefer team sizes that match the ideal number of players. For example, in a 2v2 format, avoid creating teams of 3 or more if a perfect split is possible.",
            setState: setKeepIdealTeamSize,
            default: 3,
            reset: () => setKeepIdealTeamSize(3),
        },
        {
            key: 'maximizeCourtUsage',
            label: 'Maximize court usage',
            state: maximizeCourtUsage,
            description: "Use all available courts efficiently. For example, if there are 8 players and 2 courts, prefer two full 2v2 matches over one 4v4.",
            setState: setMaximizeCourtUsage,
            default: 2,
            reset: () => setMaximizeCourtUsage(2),
        },
        {
            key: 'balanceLvl',
            label: 'Balance levels',
            state: balanceLvl,
            description: "Make matches fair by keeping total team skill levels as equal as possible. For example, a team with two beginner players shouldn’t face a team of advanced players.",
            setState: setBalanceLvl,
            default: 4,
            reset: () => setBalanceLvl(4),
        },
        {
            key: 'reduceLvlGaps',
            label: 'Reduce level gaps',
            state: reduceLvlGaps,
            description: "Minimize skill differences within teams to make each team internally balanced. For example, pairing a beginner with an advanced player would be less preferred than two intermediates together.",
            setState: setReduceLvlGaps,
            default: 1,
            reset: () => setReduceLvlGaps(1),
        },
        {
            key: 'diversifyPartners',
            label: 'Diversify partners',
            state: diversifyPartners,
            description: "Minimize repeated teammate pairings across rounds to keep teams varied. For example, if Alice has already teamed up with Bob once, prioritize assigning her a different partner in later rounds.",
            setState: setDiversifyPartners,
            default: 3,
            reset: () => setDiversifyPartners(3),
        },
        {
            key: 'diversifyOpponents',
            label: 'Diversify opponents',
            state: diversifyOpponents,
            description: "Reduce the number of times players face the same opponents across rounds. For example, if Alice played against Bob, aim to have them face different opponents in later rounds.",
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
                    <div className={styles.title}>
                        {f.description && <TooltipIcon id={f.key} description={f.description} />}
                        <span>{f.label}</span>
                        {displayWeight(f.state)}
                    </div>
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