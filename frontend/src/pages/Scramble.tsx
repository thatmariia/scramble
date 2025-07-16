import { useState } from 'react';
import Session from '../components/Session';
import Players from '../components/Players';
import Courts from '../components/Courts';
import { RoundButtons } from '../components/RoundButtons';
import SessionButtons from "../components/SessionButtons"
import RoundViz from '../components/RoundViz';

import styles from './Scramble.module.css';

export default function Scramble() {
    // sidebar collapsed state
    const [collapsed, setCollapsed] = useState(false);

    return (
        <div className={styles.page}>
            {/* <RoundViz /> */}

            <header className={`card ${styles.header}`}>
                <Session />
                <SessionButtons collapsed={collapsed} setCollapsed={setCollapsed} />
            </header>

            <div className={styles.contentRow}>  

                {/* ─── main left column: current round ─── */}
                <main className={styles.main}>
                    <RoundViz />
                    <div className={styles.actionButtons}>
                        <RoundButtons />
                    </div>
                </main>

                {/* ─── right sidebar: players & courts ─── */}
                <aside
                    className={`${styles.sidebar} ${collapsed ? styles.collapsed : ''}`}
                >
                    <Players />
                    <Courts />
                </aside>

            </div>
        </div>
    );
}