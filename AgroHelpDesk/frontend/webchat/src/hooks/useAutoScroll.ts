import { useEffect, useRef } from 'react';

/**
 * Hook for auto-scrolling to bottom of a container
 */
export const useAutoScroll = <T extends HTMLElement>(dependency: any[]) => {
    const scrollRef = useRef<T>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, dependency);

    return scrollRef;
};
