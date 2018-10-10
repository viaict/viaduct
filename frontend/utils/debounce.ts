export default function debounce (fn, delay) {
    let timeout: number;
    return function (...args) {
        if (timeout !== undefined) {
            clearTimeout(timeout)
        }
        
        timeout = setTimeout(() => fn.apply(this, args), delay)
    }
}