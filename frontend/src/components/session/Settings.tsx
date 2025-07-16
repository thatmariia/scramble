import { useState, useRef } from 'react';
import { useSessionName } from '../../context/SessionContext';
import CustomDropdown from '../../elements/CustomDropdown';
import SettingsForm from '../forms/SettingsForm';
import styles from './SessionDropdown.module.css';
import { Cog } from 'lucide-react';


export default function Settings() {
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
                <Cog className='icon' />
            </button>
            <CustomDropdown
                open={showMenu}
                onClose={() => setShowMenu(false)}
                triggerRef={menuButtonRef}
            >
                <div className={styles.dropdown}>
                    <SettingsForm close={() => setShowMenu(false)} setActive={setName} />
                </div>
            </CustomDropdown>
        </div>
    );
}