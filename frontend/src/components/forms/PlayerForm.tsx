// src/components/players/PlayerForm.tsx
import { useState } from 'react';
import type { Level } from '../../api';
import { useAddPlayer } from '../../hooks/player';
import { EntityFormWrapper } from './shared/FormWrapper';
import { CustomSelect } from '../../elements/CustomSelect';
import { LEVELS, LEVEL_VALUES, LEVEL_COLORS } from '../../constants/levels';
import style from './PlayerForm.module.css';

export function PlayerForm({ onDone }: { onDone(): void }) {
    const addPlayer = useAddPlayer();
    const [name, setName] = useState('');
    const [level, setLevel] = useState<Level>(3 as Level);

    const handleSubmit = () => {
        addPlayer.mutate(
            { name, level },
            {
                onSuccess: () => {
                    setName('');
                    setLevel(3 as Level);
                    onDone();
                },
            },
        );
    };

    return (
        <EntityFormWrapper
            onSubmit={handleSubmit}
            onCancel={onDone}
            isSubmitting={addPlayer.isPending}
        >
            <input
                className="input"
                placeholder="Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
            />
            <CustomSelect
                value={level}
                options={LEVEL_VALUES.map((lvl) => ({
                    label: LEVELS[lvl],
                    value: lvl as Level,
                    color: LEVEL_COLORS[lvl as Level],
                }))}
                onChange={(val) => setLevel(val)}
            />
        </EntityFormWrapper>
    );
}