import React, { useEffect, useRef, useState, useCallback } from 'react';

export default function Terminal({ lines, onClear }) {
  const [height, setHeight] = useState(200);
  const [dragging, setDragging] = useState(false);
  const scrollRef = useRef(null);
  const startY = useRef(0);
  const startH = useRef(0);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [lines.length]);

  const onMouseDown = useCallback((e) => {
    e.preventDefault();
    setDragging(true);
    startY.current = e.clientY;
    startH.current = height;
  }, [height]);

  useEffect(() => {
    if (!dragging) return;
    const onMove = (e) => {
      const diff = startY.current - e.clientY;
      setHeight(Math.max(80, Math.min(600, startH.current + diff)));
    };
    const onUp = () => setDragging(false);
    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseup', onUp);
    return () => {
      window.removeEventListener('mousemove', onMove);
      window.removeEventListener('mouseup', onUp);
    };
  }, [dragging]);

  return (
    <div className="terminal-wrapper">
      <div
        className="terminal-drag-handle"
        onMouseDown={onMouseDown}
        style={{
          height: 6,
          cursor: 'row-resize',
          background: dragging ? 'var(--accent)' : 'var(--border)',
          borderRadius: '3px 3px 0 0',
          transition: dragging ? 'none' : 'background 0.2s',
        }}
      />
      <div className="terminal-header">
        <h3>Terminal</h3>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>{lines.length} lines</span>
          {lines.length > 0 && (
            <button
              className="btn btn-sm"
              onClick={() => onClear()}
            >
              Clear
            </button>
          )}
        </div>
      </div>
      <div
        className="terminal-body"
        ref={scrollRef}
        style={{ height: height, maxHeight: height }}
      >
        {lines.length === 0 ? (
          <div className="terminal-line stdout" style={{ color: 'var(--text-muted)' }}>
            Click "Run" on an attack to see output here...
          </div>
        ) : (
          lines.map((line, i) => (
            <div key={i} className={`terminal-line ${line.type || 'stdout'}`}>
              {line.text}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
