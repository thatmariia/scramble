// src/components/players/PlayerForm.tsx
import { useState } from 'react';
import type { Level } from '../../api';
import { useAddPlayer, useMaxPlayerAssignment } from '../../hooks/player';
import { EntityFormWrapper } from './shared/FormWrapper';
import { CustomSelect } from '../../elements/CustomSelect';
import { LEVELS, LEVEL_VALUES, LEVEL_COLORS } from '../../constants/levels';

export function PlayerForm({ onDone }: { onDone(): void }) {
    const addPlayer = useAddPlayer();
    const [name, setName] = useState('');
    const [level, setLevel] = useState<Level>(3 as Level);
    const { data: maxAssignment, isLoading } = useMaxPlayerAssignment();

    const handleSubmit = () => {
        if (maxAssignment === undefined || isLoading) return;

        const assignment = String(maxAssignment + 1);

        addPlayer.mutate(
            { name, level, assignment },
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
            isSubmitting={addPlayer.isPending || isLoading}
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
                    slice: 3,
                }))}
                onChange={(val) => setLevel(val)}
                fixedWidth="4em"
            />
        </EntityFormWrapper>
    );
}