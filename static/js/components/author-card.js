// Add this to the END of author-card.js (replace the existing style code)

// Add component styles only if not already added
if (!document.getElementById('author-card-styles')) {
    const styleElement = document.createElement('style');
    styleElement.id = 'author-card-styles';
    styleElement.textContent = `
        .author-card-container {
            padding: 20px;
        }

        .author-header, .author-header-pro {
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 20px;
        }

        .author-header-pro {
            padding-bottom: 20px;
            border-bottom: 1px solid #e5e7eb;
        }

        .author-avatar, .author-avatar-large {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, #3b82f6, #2563eb);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 20px;
        }

        .author-avatar-large {
            width: 80px;
            height: 80px;
            font-size: 28px;
        }

        .author-primary-info {
            flex: 1;
        }

        .author-primary-info h3 {
            margin: 0 0 5px 0;
            font-size: 24px;
            color: #1f2937;
        }

        .author-title {
            font-weight: 600;
            color: #374151;
            margin: 0;
        }

        .author-org {
            color: #6b7280;
            margin: 5px 0;
        }

        .verification-badges {
            display: flex;
            gap: 8px;
            margin-top: 10px;
        }

        .badge {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
        }

        .badge.verified {
            background: #d1fae5;
            color: #065f46;
        }

        .badge.journalist {
            background: #dbeafe;
            color: #1e40af;
        }

        .badge.press {
            background: #fef3c7;
            color: #92400e;
        }

        .badge.unverified {
            background: #fee2e2;
            color: #991b1b;
        }

        .credibility-score-large {
            position: relative;
            width: 120px;
            height: 120px;
        }

        .score-label {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
        }

        .score-number {
            display: block;
            font-size: 28px;
            font-weight: 700;
            color: #1f2937;
        }

        .score-text {
            display: block;
            font-size: 11px;
            color: #6b7280;
            text-transform: uppercase;
        }

        .author-bio {
            background: #f9fafb;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }

        .author-bio h5 {
            margin: 0 0 10px 0;
            color: #1f2937;
        }

        .author-details-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }

        .detail-card {
            background: #f9fafb;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
        }

        .detail-card h6 {
            margin: 0 0 12px 0;
            color: #1f2937;
            font-size: 14px;
        }

        .experience-info {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }

        .exp-item {
            display: flex;
            justify-content: space-between;
            font-size: 13px;
        }

        .exp-label {
            color: #6b7280;
        }

        .exp-value {
            font-weight: 600;
            color: #1f2937;
        }

        .expertise-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }

        .expertise-tag {
            display: inline-block;
            background: #dbeafe;
            color: #1e40af;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
        }

        .education-list {
            margin: 0;
            padding: 0;
            list-style: none;
        }

        .education-list li {
            margin-bottom: 8px;
            font-size: 13px;
        }

        .edu-inst {
            color: #6b7280;
            font-size: 12px;
        }

        .writing-metrics {
            display: grid;
            gap: 8px;
        }

        .metric-item {
            display: flex;
            justify-content: space-between;
            font-size: 13px;
        }

        .metric-label {
            color: #6b7280;
        }

        .metric-value {
            font-weight: 500;
            color: #1f2937;
        }

        .publications-grid {
            display: grid;
            gap: 10px;
            margin-top: 10px;
        }

        .publication-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px;
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 6px;
        }

        .pub-name {
            font-weight: 600;
            color: #1f2937;
            flex: 1;
        }

        .pub-role {
            color: #6b7280;
            font-size: 12px;
        }

        .pub-count {
            background: #f3f4f6;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
            color: #6b7280;
        }

        .social-links {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 10px;
        }

        .social-link {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 12px;
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            text-decoration: none;
            color: #374151;
            font-size: 13px;
            transition: all 0.2s;
        }

        .social-link:hover {
            background: #f9fafb;
            border-color: #3b82f6;
            color: #3b82f6;
        }

        .transparency-factors {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }

        .factor-badge {
            display: inline-block;
            background: #d1fae5;
            color: #065f46;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
        }

        .fact-check-metrics {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-top: 10px;
        }

        .fc-metric {
            text-align: center;
            padding: 10px;
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 6px;
        }

        .fc-label {
            display: block;
            font-size: 12px;
            color: #6b7280;
            margin-bottom: 4px;
        }

        .fc-value {
            display: block;
            font-size: 16px;
            font-weight: 600;
        }

        .fc-value.excellent { color: #10b981; }
        .fc-value.good { color: #3b82f6; }
        .fc-value.fair { color: #f59e0b; }
        .fc-value.poor { color: #ef4444; }

        .articles-list {
            margin-top: 10px;
        }

        .article-item {
            display: grid;
            grid-template-columns: 80px 1fr auto;
            gap: 10px;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #f3f4f6;
        }

        .article-date {
            font-size: 12px;
            color: #6b7280;
        }

        .article-title {
            color: #1f2937;
            text-decoration: none;
            font-weight: 500;
        }

        .article-title:hover {
            color: #3b82f6;
            text-decoration: underline;
        }

        .article-pub {
            font-size: 12px;
            color: #6b7280;
        }

        .author-unknown-detailed {
            padding: 20px;
            background: #f9fafb;
            border-radius: 8px;
        }

        .unknown-header {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 20px;
        }

        .unknown-icon {
            font-size: 48px;
        }

        .possible-reasons ul,
        .credibility-impact ul {
            margin: 10px 0;
            padding-left: 20px;
        }

        .possible-reasons li,
        .credibility-impact li {
            margin-bottom: 5px;
            color: #4b5563;
        }

        .search-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-top: 10px;
        }

        .search-card {
            display: flex;
            flex-direction: column;
            padding: 15px;
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            text-decoration: none;
            transition: all 0.2s;
        }

        .search-card:hover {
            border-color: #3b82f6;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        .search-engine {
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 4px;
        }

        .search-description {
            font-size: 12px;
            color: #6b7280;
        }

        .no-data {
            color: #6b7280;
            font-style: italic;
            font-size: 13px;
        }

        .credibility-preview {
            margin-top: 15px;
            padding: 10px;
            background: #f9fafb;
            border-radius: 6px;
            text-align: center;
        }

        .suggestion-links {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }

        .suggestion-link {
            flex: 1;
            padding: 8px 12px;
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            text-decoration: none;
            color: #3b82f6;
            font-size: 13px;
            text-align: center;
            transition: all 0.2s;
        }

        .suggestion-link:hover {
            background: #eff6ff;
            border-color: #3b82f6;
        }
    `;
    document.head.appendChild(styleElement);
}
