import React, { useEffect, useMemo, useRef, useState, MouseEvent, ReactNode, MouseEventHandler } from 'react';

type GlowButtonProps = {
  children: ReactNode;
  onClick?: MouseEventHandler<HTMLButtonElement>;
  disabled?: boolean;
  className?: string;
};

const GlowButton: React.FC<GlowButtonProps> = ({ children, onClick, disabled = false, className = '' }) => {
  const [offsetWidth, setOffsetWidth] = useState<number>(0);
  const [offsetHeight, setOffsetHeight] = useState<number>(0);
  const [translateX, setTranslateX] = useState<string>("-40%");
  const [translateY, setTranslateY] = useState<string>("-30%");

  const buttonRef = useRef<HTMLButtonElement>(null);

  // This function calculate button's position
  const getPosition = () => {
    if (buttonRef.current) {
      setOffsetWidth(buttonRef.current.offsetWidth);
      setOffsetHeight(buttonRef.current.offsetHeight);
    }
  };

  useEffect(() => {
    getPosition();
  }, []);

  const onMove = (e: MouseEvent<HTMLButtonElement>) => {
    if (buttonRef.current && !disabled) {
      const { pageX, pageY } = e;
      const rect = buttonRef.current.getBoundingClientRect();

      setTranslateX(
        `${pageX - rect.left - window.scrollX - offsetWidth / 2}px`
      );
      setTranslateY(
        `${pageY - rect.top - window.scrollY - offsetHeight / 2}px`
      );
    }
  };

  const styleValue = useMemo(
    () => ({
      transform: `translate(${translateX}, ${translateY})`
    }),
    [translateX, translateY]
  );

  return (
    <button
      className={`glow-button ${className} ${disabled ? 'glow-button--disabled' : ''}`}
      onClick={onClick}
      onMouseMove={onMove}
      ref={buttonRef}
      disabled={disabled}
    >
      {children}
      
      <div className="glow-button__glow">
        <div className="glow-button__glow-light" style={styleValue} />
      </div>

      <div className="glow-button__border">
        <div className="glow-button__border-light" style={styleValue} />
      </div>
    </button>
  );
};

export default GlowButton;
