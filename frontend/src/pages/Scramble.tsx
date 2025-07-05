import { useState } from 'react';
import Session from '../components/Session';
import Players from '../components/Players';
import Courts from '../components/Courts';
import RoundList from '../components/RoundList';

import styles from './Scramble.module.css';

export default function Scramble() {
    // sidebar collapsed state
    const [collapsed, setCollapsed] = useState(false);

    return (
        <div className={styles.page}>
            {/* ─── top bar: session management spans full width ─── */}
            <header className={styles.header}>
                <Session />
                <button
                    className={styles.collapseBtn}
                    onClick={() => setCollapsed(!collapsed)}
                    aria-label={collapsed ? 'Open sidebar' : 'Close sidebar'}
                >
                    {collapsed ? '›' : '‹'}
                </button>
            </header>

            {/* ─── main left column: current round ─── */}
            <main className={styles.main}>
                <RoundList />
            </main>

            {/* ─── right sidebar: players & courts ─── */}
            <aside
                className={`${styles.sidebar} ${collapsed ? styles.collapsed : ''}`}
            >
                <Players />
                <Courts />
            </aside>
        </div>
    );
}