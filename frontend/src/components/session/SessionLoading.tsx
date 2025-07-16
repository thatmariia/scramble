import { useState, useRef } from 'react';
import { useSessionName } from '../../context/SessionContext';
import CustomDropdown from '../../elements/CustomDropdown';
import NewSessionForm from '../forms/NewSessionForm';
import LoadSessionForm from '../forms/LoadSessionForm';
import styles from './SessionDropdown.module.css';


export default function SessionLoading() {
    const { name: active, setName } = useSessionName();
    const [showMenu, setShowMenu] = useState(false);
    const menuButtonRef = useRef<HTMLButtonElement>(null);

    return (
        <div className={styles.menuWrapper}>
            <button
                ref={menuButtonRef}
                className="button primary"
                onClick={() => setShowMenu((v) => !v)}
            >
                <span className={styles.menuTitle}>session</span>
            </button>
            <CustomDropdown
                open={showMenu}
                onClose={() => setShowMenu(false)}
                triggerRef={menuButtonRef}
            >
                <div className={styles.dropdown}>
                    <NewSessionForm close={() => setShowMenu(false)} setActive={setName} />
                    <LoadSessionForm close={() => setShowMenu(false)} setActive={setName} />
                </div>
            </CustomDropdown>
        </div>
    );
}