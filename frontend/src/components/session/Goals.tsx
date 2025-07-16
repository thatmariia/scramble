import { useState, useRef } from 'react';
import { useSessionName } from '../../context/SessionContext';
import CustomDropdown from '../../elements/CustomDropdown';
import GoalsForm from '../forms/GoalsForm';
import styles from './SessionDropdown.module.css';
import { Target } from 'lucide-react';


export default function Goals() {
    const { name: active, setName } = useSessionName();
    const [showMenu, setShowMenu] = useState(false);
    const menuButtonRef = useRef<HTMLButtonElement>(null);

    return (
        <div className={styles.menuWrapper}>
            <button
                ref={menuButtonRef}
                className={`button ghost ${styles.settingsButton}`}
                onClick={() => setShowMenu((v) => !v)}
            >
                <Target className='icon' />
            </button>
            <CustomDropdown
                open={showMenu}
                onClose={() => setShowMenu(false)}
                triggerRef={menuButtonRef}
            >
                <div className={styles.dropdown}>
                    <p className={styles.dropdownTitle}>Imporance of goals</p>
                    <GoalsForm close={() => setShowMenu(false)} setActive={setName} />
                </div>
            </CustomDropdown>
        </div>
    );
}