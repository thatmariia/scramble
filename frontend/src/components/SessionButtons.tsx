import { useState, useRef } from 'react';
import { useSessionName } from '../context/SessionContext';
import { useSession } from '../hooks/session';
import CustomDropdown from '../elements/CustomDropdown';
import NewSessionForm from './forms/NewSessionForm';
import LoadSessionForm from './forms/LoadSessionForm';
import styles from './SessionButtons.module.css';
import { ChevronLeft, ChevronRight } from 'lucide-react';


export default function SessionButtons(
    { collapsed, setCollapsed }: { collapsed: boolean; setCollapsed: (collapsed: boolean) => void; }
) {
    const { name: active, setName } = useSessionName();
    const { isLoading } = active ? useSession(active) : { isLoading: false }; 
    const [showMenu, setShowMenu] = useState(false);
    const menuButtonRef = useRef<HTMLButtonElement>(null);

    if (!active) {
        return (
            <header className={styles.sessionHeader}>
                <div className={styles.sessionInfo}>
                    <span className={styles.name}>No active session</span>
                </div>
            </header>
        );
    }

    if (isLoading) {
        return <div className={styles.loading}>Loading session…</div>;
    }

    return (
        <div className={styles.sessionButtons}>

            
            {/* session button */}
            <div className={styles.menuWrapper}>
                <button
                    ref={menuButtonRef}
                    className={styles.menuToggle}
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

            {/* chevron */}
            <button
                className={styles.collapseBtn}
                onClick={() => setCollapsed(!collapsed)}
                aria-label={collapsed ? 'Open sidebar' : 'Close sidebar'}
            >
                {collapsed ? <ChevronLeft className='icon' /> : <ChevronRight className='icon' />}
            </button> 
        </div>
    );
}