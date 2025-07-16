import { useState, useRef } from 'react';
import { useSessionName } from '../../context/SessionContext';
import CustomDropdown from '../../elements/CustomDropdown';
import NewSessionForm from '../forms/NewSessionForm';
import LoadSessionForm from '../forms/LoadSessionForm';
import styles from './SessionDropdown.module.css';
import { CalendarDays } from 'lucide-react';


export default function SessionLoading() {
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
                <CalendarDays className='icon' />
            </button>
            <CustomDropdown
                open={showMenu}
                onClose={() => setShowMenu(false)}
                triggerRef={menuButtonRef}
            >
                <div className={styles.dropdown}>
                    <p className={styles.dropdownTitle}>Manage session</p>
                    <NewSessionForm close={() => setShowMenu(false)} setActive={setName} />
                    <LoadSessionForm close={() => setShowMenu(false)} setActive={setName} />
                </div>
            </CustomDropdown>
        </div>
    );
}