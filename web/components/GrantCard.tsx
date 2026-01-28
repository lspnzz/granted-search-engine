import { Grant } from '../lib/api';
import styles from './GrantCard.module.css';
import { CSSProperties, useEffect, useRef } from 'react';
import gsap from 'gsap';

const FORTHCOMING = "31094501";
const OPEN_FOR_SUBMISSION = "31094502";

function formatDate(dateString: string | undefined): string {
  if (!dateString) return 'N/A';
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return dateString; // Return original if parsing fails
    return new Intl.DateTimeFormat('en-GB', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    }).format(date);
  } catch (e) {
    return dateString;
  }
}

function formatCurrency(amount: string | number | undefined): string {
  if (!amount) return 'N/A';
  // If it's already a formatted string with currency, just return it (or strip and reformat if needed)
  // Assuming input might be a raw number string or proper number.
  // We'll try to parse it.
  const num = typeof amount === 'string' ? parseFloat(amount.replace(/[^0-9.-]+/g, "")) : amount;

  if (isNaN(num)) return amount.toString();

  return new Intl.NumberFormat('nl-NL', { // nl-NL uses dots for thousands and puts symbol first
    style: 'currency',
    currency: 'EUR',
    maximumFractionDigits: 0,
  }).format(num);
}

interface GrantCardProps {
  grant: Grant;
  style?: CSSProperties;
  isExpanded?: boolean;
  isDimmed?: boolean;
  onClick?: (event: React.MouseEvent) => void;
}

export default function GrantCard({ grant, style, isExpanded, isDimmed, onClick }: GrantCardProps) {
  const matchPercentage = grant.match_score ? Math.round(grant.match_score * 100) : 0;

  const cardRef = useRef<HTMLDivElement>(null);
  const metaListRef = useRef<HTMLDivElement>(null);
  const metaRowsRef = useRef<(HTMLDivElement | null)[]>([]);

  // Create a ref to store the GSAP context for cleanup
  const ctx = useRef<gsap.Context | null>(null);

  // Cleanup on unmount only
  useEffect(() => {
    ctx.current = gsap.context(() => { });
    return () => ctx.current?.revert();
  }, []);

  // Handle animation on state change
  useEffect(() => {
    ctx.current?.add(() => {
      // Animation Configuration
      const duration = 1;
      const openEase = "expo.inOut";
      const closeEase = "expo.out";

      if (isExpanded) {
        // Expand Animation
        gsap.to(cardRef.current, {
          backgroundColor: '#ffffff',
          boxShadow: '0px 8px 8px -4px rgba(9, 9, 11, 0.06), 0px 4px 4px -2px rgba(9, 9, 11, 0.03), 0px 2px 2px -1px rgba(9, 9, 11, 0.03), 0px 1px 1px -1px rgba(9, 9, 11, 0.03), 0px 1px 1px -0.5px rgba(9, 9, 11, 0.03), 0px 0px 0px 1px rgba(9, 9, 11, 0.03)',
          duration: duration,
          ease: openEase,
          overwrite: 'auto' // Ensure we kill conflicting tweens
        });

        gsap.to(metaListRef.current, {
          maxHeight: 500, // Sufficiently large value
          opacity: 1,
          y: 0,
          marginTop: 8,
          duration: duration,
          ease: openEase,
          overwrite: 'auto'
        });

        gsap.to(metaRowsRef.current, {
          opacity: 1,
          y: 0,
          duration: duration,
          // stagger: 0.05,
          ease: openEase,
          overwrite: 'auto'
        });
      } else {
        // Collapse Animation
        gsap.to(cardRef.current, {
          backgroundColor: 'transparent',
          boxShadow: 'none',
          duration: duration,
          ease: closeEase,
          overwrite: 'auto'
        });

        gsap.to(metaListRef.current, {
          maxHeight: 0,
          opacity: 0,
          marginTop: 0,
          duration: duration,
          ease: closeEase,
          overwrite: 'auto'
        });

        gsap.to(metaRowsRef.current, {
          opacity: 0,
          duration: duration,
          ease: closeEase,
          overwrite: 'auto'
        });
      }
    });
    ctx.current?.add(() => {
      gsap.to(cardRef.current, {
        opacity: isDimmed ? 0.4 : 1,
        duration: 1, // Match the main animation duration
        ease: isDimmed ? "expo.out" : "expo.in",
        overwrite: 'auto'
      });
    });
  }, [isExpanded, isDimmed]);

  return (
    <div
      ref={cardRef}
      className={`${styles.card} ${isExpanded ? styles.expanded : ''}`}
      style={style}
      onClick={onClick}
      data-card-id="true"
      data-expanded={isExpanded}
    >
      <div className={styles.mainContent}>
        <div className={styles.headerGroup}>
          <h3 className={styles.title}>{grant.title}</h3>

        </div>

        <div className={styles.footer}>
          <a href={grant.url || '#'} className={styles.sourceLink} target="_blank" rel="noopener noreferrer">
            <span className={styles.icon}>
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                <g clipPath="url(#clip0_162_7)">
                  <path d="M5.96663 3.64453L5.22697 4.40075C5.96105 4.46237 6.43936 4.68083 6.80081 5.04493C7.77405 6.02524 7.76853 7.41439 6.80639 8.38349L4.98783 10.2096C4.02016 11.1843 2.65206 11.1899 1.67883 10.2152C0.705599 9.22933 0.711157 7.8513 1.67883 6.87664L2.76885 5.77876C2.61313 5.42584 2.57421 5.00572 2.63538 4.64162L1.00035 6.2829C-0.328813 7.62725 -0.339936 9.53179 1.00591 10.8874C2.35732 12.2486 4.24817 12.2374 5.57733 10.8986L7.47929 8.97723C8.81404 7.63288 8.82514 5.72832 7.47376 4.37274C7.12336 4.01984 6.67848 3.76777 5.96663 3.64453ZM5.82762 8.26022L6.56726 7.50404C5.83314 7.448 5.35488 7.22395 4.99339 6.85983C4.02016 5.87954 4.02572 4.49037 4.98783 3.5213L6.80081 1.69518C7.77405 0.720508 9.14217 0.714904 10.1154 1.69518C11.0886 2.67546 11.0775 4.05905 10.1154 5.02813L9.02537 6.12602C9.18107 6.48452 9.21444 6.89907 9.15886 7.26319L10.7939 5.6219C12.123 4.27752 12.1342 2.37858 10.7883 1.01739C9.43688 -0.343796 7.54603 -0.332593 6.21133 1.01179L4.31491 2.92753C2.98019 4.27191 2.96906 6.17644 4.32047 7.53204C4.67084 7.88492 5.11574 8.13701 5.82762 8.26022Z" fill="currentColor" />
                </g>
                <defs>
                  <clipPath id="clip0_162_7">
                    <rect width="12" height="12" fill="white" />
                  </clipPath>
                </defs>
              </svg>

            </span>
            Source: EU Funding & Tenders Portal
          </a>

          {matchPercentage > 0 && (
            <div className={styles.matchScore}>
              <span className={styles.icon}>
                <svg width="16" height="14" viewBox="0 0 16 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <g clipPath="url(#clip0_26_1524)">
                    <path d="M7.86569 0C3.51943 0 0 3.61431 0 8.07773C0 10.2768 0.855122 12.2945 2.27561 13.7605C2.5159 14.0073 2.89046 14.0218 3.159 13.7678C3.37809 13.5428 3.33569 13.1508 3.053 12.8388C1.91519 11.6195 1.22261 9.92119 1.22261 8.07773C1.22261 4.26023 4.15547 1.2338 7.86569 1.2338C11.5831 1.2338 14.5159 4.26023 14.5159 8.07773C14.5159 9.92119 13.8233 11.6195 12.6855 12.8388C12.4028 13.1508 12.3604 13.5428 12.5795 13.7678C12.848 14.0218 13.2226 14.0073 13.4629 13.7605C14.8834 12.2945 15.7385 10.2768 15.7385 8.07773C15.7385 3.61431 12.2191 0 7.86569 0Z" fill="currentColor" />
                    <path d="M6.18469 4.88428C4.98329 4.88428 4.12109 5.81326 4.12109 7.09785C4.12109 9.00659 6.07869 10.7629 7.52746 11.7065C7.64759 11.779 7.80303 11.8734 7.89494 11.8734C7.97975 11.8734 8.12109 11.779 8.22711 11.7065C9.66172 10.7412 11.6334 9.00659 11.6334 7.09785C11.6334 5.81326 10.7713 4.88428 9.5769 4.88428C8.82783 4.88428 8.2271 5.32699 7.88083 5.98744C7.52746 5.32699 6.94088 4.88428 6.18469 4.88428Z" fill="currentColor" />
                  </g>
                  <defs>
                    <clipPath id="clip0_26_1524">
                      <rect width="16" height="14" fill="white" />
                    </clipPath>
                  </defs>
                </svg>

              </span>
              {matchPercentage}% Match
            </div>
          )}
        </div>
      </div>

      {/* META ROWS: Plain text below card */}
      <div className={styles.metaList} ref={metaListRef}>
        <div
          ref={(el) => { metaRowsRef.current[0] = el; }}
          className={styles.metaRow}
        >
          <div className={styles.metaLabelGroup}>
            <span className={styles.icon}>
              <svg width="16" height="14" viewBox="0 0 16 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                <g clipPath="url(#clip0_119_389)">
                  <path d="M15.7571 7.84477C15.7571 3.72372 12.5911 0.341868 8.56164 0.0017202C8.35232 -0.0179037 8.19531 0.132546 8.19531 0.341868V2.48087C8.19531 2.65749 8.31963 2.79485 8.4962 2.80794C11.0016 3.11538 12.9508 5.25438 12.9508 7.84477C12.9508 9.02219 12.5453 10.1081 11.8323 11.0173C11.7407 11.1285 11.7473 11.2723 11.8453 11.377L13.4087 12.9339C13.5527 13.0778 13.7751 13.0778 13.9059 12.9208C15.0637 11.5471 15.7571 9.77441 15.7571 7.84477Z" fill="currentColor" />
                  <path d="M0 7.84477C0 9.78097 0.69338 11.5537 1.85119 12.9273C1.98201 13.0843 2.19788 13.0778 2.34833 12.9339L3.91169 11.377C4.00982 11.2723 4.01635 11.1285 3.92478 11.0173C3.20524 10.1081 2.80621 9.02219 2.80621 7.84477C2.80621 5.25438 4.75552 3.11538 7.26081 2.80794C7.43744 2.79485 7.56176 2.65749 7.56176 2.48087V0.341868C7.56176 0.132546 7.40476 -0.0179037 7.19544 0.0017202C3.16599 0.341868 0 3.72372 0 7.84477Z" fill="currentColor" />
                  <path d="M8.67467 10.8078C8.85787 10.8078 9.08026 10.8012 9.26339 10.762C9.45965 10.7097 9.61665 10.6115 9.61665 10.4153C9.61665 10.206 9.47271 10.1079 9.26339 10.1079C9.04757 10.1079 8.96906 10.134 8.71393 10.134C7.30099 10.134 6.43757 9.33599 6.43757 7.90342C6.43757 6.49707 7.24868 5.66633 8.6943 5.66633C8.92325 5.66633 9.126 5.69249 9.26339 5.69249C9.47271 5.69249 9.61665 5.58783 9.61665 5.37851C9.61665 5.19535 9.4989 5.08415 9.26339 5.02528C9.10645 4.99257 8.90362 4.97949 8.67467 4.97949C7.03279 4.97949 5.65261 5.91489 5.65261 7.89692C5.65261 9.76769 6.88891 10.8078 8.67467 10.8078ZM4.76953 7.30821C4.76953 7.42597 4.86765 7.52403 4.9854 7.52403H8.60273C8.72049 7.52403 8.81862 7.42597 8.81862 7.30821C8.81862 7.18389 8.72049 7.08576 8.60273 7.08576H4.9854C4.86765 7.08576 4.76953 7.18389 4.76953 7.30821ZM4.76953 8.47907C4.76953 8.59683 4.86765 8.69496 4.9854 8.69496H8.60273C8.72049 8.69496 8.81862 8.59683 8.81862 8.47907C8.81862 8.36132 8.72049 8.26325 8.60273 8.26325H4.9854C4.86765 8.26325 4.76953 8.36132 4.76953 8.47907Z" fill="currentColor" />
                </g>
                <defs>
                  <clipPath id="clip0_119_389">
                    <rect width="16" height="13.0664" fill="white" />
                  </clipPath>
                </defs>
              </svg>
            </span>
            Total available funding
          </div>
          <span className={styles.metaValue}>{formatCurrency(grant.amount)}</span>
        </div>

        <div
          ref={(el) => { metaRowsRef.current[1] = el; }}
          className={styles.metaRow}
        >
          <div className={styles.metaLabelGroup}>
            <span className={styles.icon}>
              <svg width="16" height="14" viewBox="0 0 16 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                <g clipPath="url(#clip0_166_74)">
                  <path d="M2.43529 13.9999H13.0296C14.6506 13.9999 15.4571 13.21 15.4571 11.6451V2.37C15.4571 0.805155 14.6506 0.0151367 13.0296 0.0151367H2.43529C0.81435 0.0151367 0 0.797558 0 2.37V11.6451C0 13.2175 0.81435 13.9999 2.43529 13.9999ZM2.31896 12.7769C1.6287 12.7769 1.24868 12.42 1.24868 11.7135V4.55015C1.24868 3.85128 1.6287 3.48666 2.31896 3.48666H13.1304C13.8206 3.48666 14.2084 3.85128 14.2084 4.55015V11.7135C14.2084 12.42 13.8206 12.7769 13.1304 12.7769H2.31896Z" fill="currentColor" />
                  <path d="M8.1121 11.4704C8.47662 11.4704 8.68603 11.2349 8.68603 10.8399V5.43128C8.68603 5.02867 8.46886 4.80078 8.08108 4.80078C7.81738 4.80078 7.63124 4.86916 7.32877 5.07426L6.04133 5.93264C5.88622 6.03899 5.81641 6.14533 5.81641 6.32765C5.81641 6.54034 5.99479 6.73785 6.22747 6.73785C6.32828 6.73785 6.40584 6.72265 6.56872 6.61631L7.4994 6.01619H7.54594V10.8399C7.54594 11.2349 7.75534 11.4704 8.1121 11.4704Z" fill="currentColor" />
                </g>
                <defs>
                  <clipPath id="clip0_166_74">
                    <rect width="16" height="14" fill="white" />
                  </clipPath>
                </defs>
              </svg>

            </span>
            Opening date
          </div>
          <span className={styles.metaValue}>{formatDate(grant.opening_date)}</span>
        </div>

        <div
          ref={(el) => { metaRowsRef.current[2] = el; }}
          className={styles.metaRow}
        >
          <div className={styles.metaLabelGroup}>
            <span className={styles.icon}>
              <svg width="16" height="14" viewBox="0 0 16 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                <g clipPath="url(#clip0_165_61)">
                  <path d="M2.43529 13.9999H13.0296C14.6506 13.9999 15.4571 13.21 15.4571 11.6451V2.37C15.4571 0.805155 14.6506 0.0151367 13.0296 0.0151367H2.43529C0.81435 0.0151367 0 0.797558 0 2.37V11.6451C0 13.2175 0.81435 13.9999 2.43529 13.9999ZM2.31896 12.7769C1.6287 12.7769 1.24868 12.42 1.24868 11.7135V4.55015C1.24868 3.85128 1.6287 3.48666 2.31896 3.48666H13.1304C13.8206 3.48666 14.2084 3.85128 14.2084 4.55015V11.7135C14.2084 12.42 13.8206 12.7769 13.1304 12.7769H2.31896Z" fill="currentColor" fillOpacity="1" />
                  <path d="M11.3531 9.2293C11.9736 9.2293 12.4776 8.73555 12.4776 8.12783C12.4776 7.52013 11.9736 7.02637 11.3531 7.02637C10.7326 7.02637 10.2285 7.52013 10.2285 8.12783C10.2285 8.73555 10.7326 9.2293 11.3531 9.2293Z" fill="currentColor" fillOpacity="1" />
                  <path d="M7.732 9.2293C8.35245 9.2293 8.85658 8.73555 8.85658 8.12783C8.85658 7.52013 8.35245 7.02637 7.732 7.02637C7.1193 7.02637 6.60742 7.52013 6.60742 8.12783C6.60742 8.73555 7.1193 9.2293 7.732 9.2293Z" fill="currentColor" fillOpacity="1" />
                  <path d="M4.11872 9.2293C4.73918 9.2293 5.2433 8.73555 5.2433 8.12783C5.2433 7.52013 4.73142 7.02637 4.11872 7.02637C3.49827 7.02637 2.99414 7.52013 2.99414 8.12783C2.99414 8.73555 3.49827 9.2293 4.11872 9.2293Z" fill="currentColor" fillOpacity="1" />
                </g>
                <defs>
                  <clipPath id="clip0_165_61">
                    <rect width="16" height="14" fill="white" />
                  </clipPath>
                </defs>
              </svg>

            </span>
            Deadline date
          </div>
          <span className={styles.metaValue}>{formatDate(grant.deadline)}</span>
        </div>

        <div
          ref={(el) => { metaRowsRef.current[3] = el; }}
          className={styles.metaRow}
        >
          <div className={styles.metaLabelGroup}>
            <span className={styles.icon}>
              <svg width="16" height="11" viewBox="0 0 16 11" fill="none" xmlns="http://www.w3.org/2000/svg">
                <g clipPath="url(#clip0_172_102)">
                  <path d="M5.00164 2.42639H10.5371C10.7149 2.42639 10.8534 2.29122 10.8534 2.111C10.8534 1.94365 10.7149 1.80849 10.5371 1.80849H5.00164C4.82371 1.80849 4.68532 1.94365 4.68532 2.111C4.68532 2.29122 4.82371 2.42639 5.00164 2.42639ZM4.1252 3.91323H11.4134C11.5979 3.91323 11.7429 3.77162 11.7429 3.59784C11.7429 3.42405 11.5979 3.26314 11.4134 3.26314H4.1252C3.94068 3.26314 3.79571 3.42405 3.79571 3.59784C3.79571 3.77162 3.94068 3.91323 4.1252 3.91323ZM2.06918 10.9998H13.4695C14.8533 10.9998 15.5386 10.3305 15.5386 9.00452V5.45156C15.5386 4.87227 15.4464 4.60194 15.1631 4.22862L12.8896 1.22276C12.1713 0.263719 11.7759 0.0126953 10.6029 0.0126953H4.93574C3.76276 0.0126953 3.37396 0.263719 2.65567 1.22276L0.375616 4.22862C0.0988465 4.60194 0 4.87227 0 5.45156V9.00452C0 10.3369 0.691925 10.9998 2.06918 10.9998ZM7.76934 7.27309C6.78087 7.27309 6.14825 6.43635 6.14825 5.64465V5.62534C6.14825 5.3357 5.97033 5.06536 5.60131 5.06536H1.40362C1.18616 5.06536 1.14003 4.88515 1.24546 4.74354L3.68368 1.47379C3.98681 1.06185 4.3756 0.913808 4.85666 0.913808H10.6821C11.1631 0.913808 11.5519 1.06185 11.855 1.47379L14.2932 4.74354C14.3921 4.88515 14.3525 5.06536 14.1351 5.06536H9.93738C9.56834 5.06536 9.39701 5.3357 9.39701 5.62534V5.64465C9.39701 6.43635 8.7644 7.27309 7.76934 7.27309Z" fill="#FF594A" />
                </g>
                <defs>
                  <clipPath id="clip0_172_102">
                    <rect width="16" height="11" fill="white" />
                  </clipPath>
                </defs>
              </svg>
            </span>
            Status
          </div>
          <span className={styles.metaValue}>
            {grant.status === FORTHCOMING ? 'Forthcoming' :
              grant.status === OPEN_FOR_SUBMISSION ? 'Open for submission' :
                grant.status || 'Open for submissions'}
          </span>
        </div>
      </div>
    </div>
  );
}
