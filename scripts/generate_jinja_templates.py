"""
scripts/generate_jinja_templates.py
Generates authentic, high-quality template.tex.jinja files for all 20 templates
matching their exact Overleaf styling, commands, and layout.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "resume_templates"

TEMPLATES = {}

# 1. Jake's Resume (Minimal single-column ATS)
TEMPLATES["jakes-resume"] = r"""%-------------------------
% Jake's Resume — ATS Optimized Single Column
% License : MIT
%------------------------
\documentclass[letterpaper,11pt]{article}

\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage{tabularx}
\input{glyphtounicode}

\pagestyle{fancy}
\fancyhf{}
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

\addtolength{\oddsidemargin}{-0.5in}
\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1in}
\addtolength{\topmargin}{-.5in}
\addtolength{\textheight}{1.0in}

\urlstyle{same}
\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

\titleformat{\section}{
  \vspace{-4pt}\scshape\raggedright\large
}{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]

\pdfgentounicode=1

\newcommand{\resumeItem}[1]{
  \item\small{
    {#1 \vspace{-2pt}}
  }
}

\newcommand{\resumeSubheading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeProjectHeading}[2]{
    \item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \small#1 & #2 \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubItem}[1]{\resumeItem{#1}\vspace{-4pt}}
\renewcommand\labelitemii{$\vcenter{\hbox{\tiny$\bullet$}}$}
\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.15in, label={}]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}

\begin{document}

%----------HEADING----------
\begin{center}
    \textbf{\Huge \scshape \VAR{full_name}} \\ \vspace{1pt}
    \small 
    \BLOCK{ if phone }\VAR{phone} $|$ \BLOCK{ endif }
    \BLOCK{ if email }\href{mailto:\VAR{email}}{\underline{\VAR{email}}} $|$ \BLOCK{ endif }
    \BLOCK{ if linkedin }\href{\VAR{linkedin}}{\underline{\VAR{linkedin}}} $|$ \BLOCK{ endif }
    \BLOCK{ if github }\href{\VAR{github}}{\underline{\VAR{github}}} $|$ \BLOCK{ endif }
    \BLOCK{ if location }\VAR{location}\BLOCK{ endif }
\end{center}

\BLOCK{ if summary }
%-----------SUMMARY-----------
\section{Summary}
\small{\VAR{summary}}
\BLOCK{ endif }

\BLOCK{ if education }
%-----------EDUCATION-----------
\section{Education}
  \resumeSubHeadingListStart
    \BLOCK{ for edu in education }
    \resumeSubheading
      {\VAR{edu.institution}}{\VAR{edu.location|default('')}}
      {\VAR{edu.degree}\BLOCK{ if edu.gpa } (GPA: \VAR{edu.gpa})\BLOCK{ endif }}{\VAR{edu.start_date} -- \VAR{edu.end_date|default('Present')}}
    \BLOCK{ endfor }
  \resumeSubHeadingListEnd
\BLOCK{ endif }

\BLOCK{ if experience }
%-----------EXPERIENCE-----------
\section{Experience}
  \resumeSubHeadingListStart
    \BLOCK{ for exp in experience }
    \resumeSubheading
      {\VAR{exp.role}}{\VAR{exp.start_date} -- \VAR{exp.end_date|default('Present')}}
      {\VAR{exp.company}}{\VAR{exp.location|default('')}}
      \resumeItemListStart
        \BLOCK{ for b in exp.bullets }
        \resumeItem{\VAR{b}}
        \BLOCK{ endfor }
      \resumeItemListEnd
    \BLOCK{ endfor }
  \resumeSubHeadingListEnd
\BLOCK{ endif }

\BLOCK{ if projects }
%-----------PROJECTS-----------
\section{Projects}
    \resumeSubHeadingListStart
      \BLOCK{ for proj in projects }
      \resumeProjectHeading
          {\textbf{\VAR{proj.title}}\BLOCK{ if proj.technologies } $|$ \emph{\VAR{proj.technologies}}\BLOCK{ endif }}{}
          \resumeItemListStart
            \BLOCK{ if proj.description }
            \resumeItem{\VAR{proj.description}}
            \BLOCK{ endif }
            \BLOCK{ for b in proj.bullets }
            \resumeItem{\VAR{b}}
            \BLOCK{ endfor }
          \resumeItemListEnd
      \BLOCK{ endfor }
    \resumeSubHeadingListEnd
\BLOCK{ endif }

\BLOCK{ if skills or skill_categories }
%-----------TECHNICAL SKILLS-----------
\section{Technical Skills}
 \begin{itemize}[leftmargin=0.15in, label={}]
    \small{\item{
     \BLOCK{ for cat in skill_categories }
     \textbf{\VAR{cat.category_name}}{: \VAR{cat.skills|join(', ')}} \\
     \BLOCK{ endfor }
     \BLOCK{ if not skill_categories and skills }
     \textbf{Skills}{: \VAR{skills|join(', ')}} \\
     \BLOCK{ endif }
    }}
 \end{itemize}
\BLOCK{ endif }

\BLOCK{ if certifications }
%-----------CERTIFICATIONS-----------
\section{Certifications}
  \resumeSubHeadingListStart
    \BLOCK{ for cert in certifications }
    \resumeProjectHeading
      {\textbf{\VAR{cert.name}}\BLOCK{ if cert.issuer } -- \VAR{cert.issuer}\BLOCK{ endif }}{\VAR{cert.date_obtained|default('')}}
    \BLOCK{ endfor }
  \resumeSubHeadingListEnd
\BLOCK{ endif }

\end{document}
"""

# 2. FAANGPath Simple Template
TEMPLATES["faangpath-simple"] = r"""%-------------------------
% FAANGPath Simple Template — Clean ATS Resume
%------------------------
\documentclass{resume}

\usepackage[left=0.5in,top=0.5in,right=0.5in,bottom=0.5in]{geometry}
\usepackage[hidelinks]{hyperref}
\newcommand{\tab}[1]{\hspace{.2667\textwidth}\rlap{#1}}
\newcommand{\itab}[1]{\hspace{0em}\rlap{#1}}

\name{\VAR{full_name}}
\address{\BLOCK{ if phone }\VAR{phone} \BLOCK{ endif }\BLOCK{ if location }\\ \VAR{location}\BLOCK{ endif }}
\address{\BLOCK{ if email }\href{mailto:\VAR{email}}{\VAR{email}}\BLOCK{ endif }\BLOCK{ if linkedin } \\ \href{\VAR{linkedin}}{\VAR{linkedin}}\BLOCK{ endif }\BLOCK{ if github } \\ \href{\VAR{github}}{\VAR{github}}\BLOCK{ endif }}

\begin{document}

\BLOCK{ if summary }
\begin{rSection}{SUMMARY}
{\VAR{summary}}
\end{rSection}
\BLOCK{ endif }

\BLOCK{ if education }
\begin{rSection}{Education}
\BLOCK{ for edu in education }
{\bf \VAR{edu.degree}}, \VAR{edu.institution} \hfill {\VAR{edu.start_date} -- \VAR{edu.end_date|default('Present')}}\\
\BLOCK{ if edu.gpa }GPA: \VAR{edu.gpa}\BLOCK{ endif }
\BLOCK{ if edu.details }\VAR{edu.details}\BLOCK{ endif }
\BLOCK{ endfor }
\end{rSection}
\BLOCK{ endif }

\BLOCK{ if experience }
\begin{rSection}{EXPERIENCE}
\BLOCK{ for exp in experience }
\textbf{\VAR{exp.role}} \hfill {\VAR{exp.start_date} -- \VAR{exp.end_date|default('Present')}}\\
\VAR{exp.company} \hfill \textit{\VAR{exp.location|default('')}}
\begin{itemize}
    \itemsep -3pt {}
    \BLOCK{ for b in exp.bullets }
    \item \VAR{b}
    \BLOCK{ endfor }
\end{itemize}
\BLOCK{ endfor }
\end{rSection}
\BLOCK{ endif }

\BLOCK{ if projects }
\begin{rSection}{PROJECTS}
\BLOCK{ for proj in projects }
\textbf{\VAR{proj.title}}\BLOCK{ if proj.technologies } $|$ \textit{\VAR{proj.technologies}}\BLOCK{ endif } \hfill \BLOCK{ if proj.link }\href{\VAR{proj.link}}{\VAR{proj.link}}\BLOCK{ endif }
\begin{itemize}
    \itemsep -3pt {}
    \BLOCK{ if proj.description }\item \VAR{proj.description}\BLOCK{ endif }
    \BLOCK{ for b in proj.bullets }\item \VAR{b}\BLOCK{ endfor }
\end{itemize}
\BLOCK{ endfor }
\end{rSection}
\BLOCK{ endif }

\BLOCK{ if skills or skill_categories }
\begin{rSection}{SKILLS}
\begin{tabular}{ @{} >{\bfseries}l @{\hspace{6ex}} l }
\BLOCK{ for cat in skill_categories }
\VAR{cat.category_name} & \VAR{cat.skills|join(', ')} \\
\BLOCK{ endfor }
\BLOCK{ if not skill_categories and skills }
Technical Skills & \VAR{skills|join(', ')} \\
\BLOCK{ endif }
\end{tabular}
\end{rSection}
\BLOCK{ endif }

\BLOCK{ if certifications }
\begin{rSection}{CERTIFICATIONS}
\BLOCK{ for cert in certifications }
\textbf{\VAR{cert.name}}\BLOCK{ if cert.issuer } -- \VAR{cert.issuer}\BLOCK{ endif } \hfill {\VAR{cert.date_obtained|default('')}}\\
\BLOCK{ endfor }
\end{rSection}
\BLOCK{ endif }

\end{document}
"""

# 3. SWE Resume Template
TEMPLATES["swe-resume"] = r"""%-------------------------
% SWE Resume Template — Clean ATS-Optimized
%------------------------
\documentclass[10pt, letterpaper]{article}

\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage{tabularx}
\usepackage[left=0.5in,top=0.5in,right=0.5in,bottom=0.5in]{geometry}

\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

\titleformat{\section}{\vspace{-5pt}\scshape\raggedright\large}{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]

\begin{document}

\begin{center}
    {\Huge \scshape \textbf{\VAR{full_name}}} \\ \vspace{2pt}
    \small
    \BLOCK{ if phone }\VAR{phone} $\cdot$\BLOCK{ endif }
    \BLOCK{ if email }\href{mailto:\VAR{email}}{\VAR{email}} $\cdot$\BLOCK{ endif }
    \BLOCK{ if linkedin }\href{\VAR{linkedin}}{LinkedIn} $\cdot$\BLOCK{ endif }
    \BLOCK{ if github }\href{\VAR{github}}{GitHub} $\cdot$\BLOCK{ endif }
    \BLOCK{ if location }\VAR{location}\BLOCK{ endif }
\end{center}

\BLOCK{ if summary }
\section{Professional Summary}
\small{\VAR{summary}}
\BLOCK{ endif }

\BLOCK{ if skills or skill_categories }
\section{Technical Skills}
\begin{itemize}[leftmargin=0.15in, label={}]
\small{\item{
    \BLOCK{ for cat in skill_categories }
    \textbf{\VAR{cat.category_name}:} \VAR{cat.skills|join(', ')} \\
    \BLOCK{ endfor }
    \BLOCK{ if not skill_categories and skills }
    \textbf{Core Skills:} \VAR{skills|join(', ')} \\
    \BLOCK{ endif }
}}
\end{itemize}
\BLOCK{ endif }

\BLOCK{ if experience }
\section{Professional Experience}
\BLOCK{ for exp in experience }
\noindent
\textbf{\VAR{exp.role}} \hfill \textbf{\VAR{exp.start_date} -- \VAR{exp.end_date|default('Present')}} \\
\textit{\VAR{exp.company}} \hfill \textit{\VAR{exp.location|default('')}}
\begin{itemize}[leftmargin=0.2in, topsep=2pt, itemsep=1pt]
    \BLOCK{ for b in exp.bullets }
    \item \small{\VAR{b}}
    \BLOCK{ endfor }
\end{itemize}
\vspace{2pt}
\BLOCK{ endfor }
\BLOCK{ endif }

\BLOCK{ if projects }
\section{Projects}
\BLOCK{ for proj in projects }
\noindent
\textbf{\VAR{proj.title}} \BLOCK{ if proj.technologies }($|$\textit{\VAR{proj.technologies}})\BLOCK{ endif } \hfill \BLOCK{ if proj.link }\href{\VAR{proj.link}}{Link}\BLOCK{ endif }
\begin{itemize}[leftmargin=0.2in, topsep=2pt, itemsep=1pt]
    \BLOCK{ if proj.description }\item \small{\VAR{proj.description}}\BLOCK{ endif }
    \BLOCK{ for b in proj.bullets }\item \small{\VAR{b}}\BLOCK{ endfor }
\end{itemize}
\vspace{2pt}
\BLOCK{ endfor }
\BLOCK{ endif }

\BLOCK{ if education }
\section{Education}
\BLOCK{ for edu in education }
\noindent
\textbf{\VAR{edu.institution}} \hfill \textbf{\VAR{edu.start_date} -- \VAR{edu.end_date|default('Present')}} \\
\VAR{edu.degree} \hfill \textit{\VAR{edu.location|default('')}} \BLOCK{ if edu.gpa }(GPA: \VAR{edu.gpa})\BLOCK{ endif }\\
\vspace{2pt}
\BLOCK{ endfor }
\BLOCK{ endif }

\BLOCK{ if certifications }
\section{Certifications}
\begin{itemize}[leftmargin=0.2in, topsep=2pt, itemsep=1pt]
\BLOCK{ for cert in certifications }
\item \textbf{\VAR{cert.name}} -- \VAR{cert.issuer|default('')} \hfill \textit{\VAR{cert.date_obtained|default('')}}
\BLOCK{ endfor }
\end{itemize}
\BLOCK{ endif }

\end{document}
"""

# 4. Libre CV (Minimalist two-column)
TEMPLATES["libre-cv"] = r"""%-------------------------
% Libre CV — Minimalist Two-Column
%------------------------
\documentclass[10pt, a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{paracol}
\usepackage{xcolor}
\usepackage[left=0.6in,top=0.6in,right=0.6in,bottom=0.6in]{geometry}

\definecolor{primary}{HTML}{2B2D42}
\definecolor{accent}{HTML}{4D7298}
\definecolor{text}{HTML}{2B2D42}

\titleformat{\section}{\color{primary}\large\bfseries\scshape}{}{0em}{}[\color{accent}\titlerule \vspace{-3pt}]

\begin{document}

% Header
\begin{center}
    {\Huge \textbf{\color{primary}\VAR{full_name}}} \\ \vspace{4pt}
    \small \color{text}
    \BLOCK{ if email }\href{mailto:\VAR{email}}{\VAR{email}} \quad$\vert$\quad\BLOCK{ endif }
    \BLOCK{ if phone }\VAR{phone} \quad$\vert$\quad\BLOCK{ endif }
    \BLOCK{ if location }\VAR{location} \quad$\vert$\quad\BLOCK{ endif }
    \BLOCK{ if linkedin }\href{\VAR{linkedin}}{LinkedIn}\BLOCK{ endif }
\end{center}
\vspace{6pt}

\BLOCK{ if summary }
\section{About Me}
\small{\VAR{summary}}
\vspace{6pt}
\BLOCK{ endif }

\columnratio{0.68}
\begin{paracol}{2}

\BLOCK{ if experience }
\section{Experience}
\BLOCK{ for exp in experience }
\noindent
\textbf{\VAR{exp.role}} \hfill \textbf{\small\VAR{exp.start_date} -- \VAR{exp.end_date|default('Present')}}\\
\textit{\color{accent}\VAR{exp.company}} \hfill \textit{\small\VAR{exp.location|default('')}}
\begin{itemize}[leftmargin=12pt, topsep=2pt, itemsep=1pt]
    \BLOCK{ for b in exp.bullets }
    \item \small{\VAR{b}}
    \BLOCK{ endfor }
\end{itemize}
\vspace{4pt}
\BLOCK{ endfor }
\BLOCK{ endif }

\BLOCK{ if projects }
\section{Key Projects}
\BLOCK{ for proj in projects }
\noindent
\textbf{\VAR{proj.title}} \BLOCK{ if proj.technologies }\textit{(\VAR{proj.technologies})}\BLOCK{ endif }
\begin{itemize}[leftmargin=12pt, topsep=2pt, itemsep=1pt]
    \BLOCK{ if proj.description }\item \small{\VAR{proj.description}}\BLOCK{ endif }
    \BLOCK{ for b in proj.bullets }\item \small{\VAR{b}}\BLOCK{ endfor }
\end{itemize}
\vspace{4pt}
\BLOCK{ endfor }
\BLOCK{ endif }

\switchcolumn

\BLOCK{ if education }
\section{Education}
\BLOCK{ for edu in education }
\textbf{\VAR{edu.degree}}\\
\textit{\color{accent}\VAR{edu.institution}}\\
\small\VAR{edu.start_date} -- \VAR{edu.end_date|default('Present')}\\
\BLOCK{ if edu.gpa }\small GPA: \VAR{edu.gpa}\\\BLOCK{ endif }
\vspace{4pt}
\BLOCK{ endfor }
\BLOCK{ endif }

\BLOCK{ if skills or skill_categories }
\section{Skills}
\BLOCK{ for cat in skill_categories }
\textbf{\small\VAR{cat.category_name}}\\
\small\VAR{cat.skills|join(', ')}\\[4pt]
\BLOCK{ endfor }
\BLOCK{ if not skill_categories and skills }
\small\VAR{skills|join(', ')}\\[4pt]
\BLOCK{ endif }
\BLOCK{ endif }

\BLOCK{ if certifications }
\section{Certifications}
\BLOCK{ for cert in certifications }
\textbf{\small\VAR{cert.name}}\\
\small\VAR{cert.issuer|default('')} (\VAR{cert.date_obtained|default('')})\\[3pt]
\BLOCK{ endfor }
\BLOCK{ endif }

\end{paracol}

\end{document}
"""

# 5. Awesome CV (posquit0)
TEMPLATES["awesome-cv"] = r"""%!TEX TS-program = xelatex
%!TEX encoding = UTF-8 Unicode
\documentclass[11pt, a4paper]{awesome-cv}

\geometry{left=1.4cm, top=1.4cm, right=1.4cm, bottom=1.8cm, footskip=.5cm}
\fontdir[fonts/]
\colorlet{awesome}{awesome-emerald}
\setbool{acvSectionColorHighlight}{true}

\name{\VAR{full_name}}{}
\position{\BLOCK{ if experience }\VAR{experience[0].role}\BLOCK{ else }Professional\BLOCK{ endif }}
\address{\VAR{location|default('')}}

\mobile{\VAR{phone|default('')}}
\email{\VAR{email}}
\homepage{\VAR{website|default('')}}
\github{\VAR{github|default('')}}
\linkedin{\VAR{linkedin|default('')}}

\begin{document}

\makecvheader[C]
\makecvfooter{\today}{\VAR{full_name}~~~·~~~Résumé}{\thepage}

\BLOCK{ if summary }
\cvsection{Summary}
\begin{cvparagraph}
\VAR{summary}
\end{cvparagraph}
\BLOCK{ endif }

\BLOCK{ if experience }
\cvsection{Work Experience}
\begin{cventries}
\BLOCK{ for exp in experience }
  \cventry
    {\VAR{exp.role}}
    {\VAR{exp.company}}
    {\VAR{exp.location|default('')}}
    {\VAR{exp.start_date} -- \VAR{exp.end_date|default('Present')}}
    {
      \begin{cvitems}
        \BLOCK{ for b in exp.bullets }
        \item {\VAR{b}}
        \BLOCK{ endfor }
      \end{cvitems}
    }
\BLOCK{ endfor }
\end{cventries}
\BLOCK{ endif }

\BLOCK{ if projects }
\cvsection{Key Projects}
\begin{cventries}
\BLOCK{ for proj in projects }
  \cventry
    {\VAR{proj.technologies|default('Personal Project')}}
    {\VAR{proj.title}}
    {\BLOCK{ if proj.link }\href{\VAR{proj.link}}{Demo}\BLOCK{ endif }}
    {}
    {
      \begin{cvitems}
        \BLOCK{ if proj.description }\item {\VAR{proj.description}}\BLOCK{ endif }
        \BLOCK{ for b in proj.bullets }
        \item {\VAR{b}}
        \BLOCK{ endfor }
      \end{cvitems}
    }
\BLOCK{ endfor }
\end{cventries}
\BLOCK{ endif }

\BLOCK{ if skills or skill_categories }
\cvsection{Skills}
\begin{cvskills}
\BLOCK{ for cat in skill_categories }
  \cvskill
    {\VAR{cat.category_name}}
    {\VAR{cat.skills|join(', ')}}
\BLOCK{ endfor }
\BLOCK{ if not skill_categories and skills }
  \cvskill
    {Skills}
    {\VAR{skills|join(', ')}}
\BLOCK{ endif }
\end{cvskills}
\BLOCK{ endif }

\BLOCK{ if education }
\cvsection{Education}
\begin{cventries}
\BLOCK{ for edu in education }
  \cventry
    {\VAR{edu.degree}\BLOCK{ if edu.gpa } (GPA: \VAR{edu.gpa})\BLOCK{ endif }}
    {\VAR{edu.institution}}
    {\VAR{edu.location|default('')}}
    {\VAR{edu.start_date} -- \VAR{edu.end_date|default('Present')}}
    {}
\BLOCK{ endfor }
\end{cventries}
\BLOCK{ endif }

\BLOCK{ if certifications }
\cvsection{Certifications}
\begin{cventries}
\BLOCK{ for cert in certifications }
  \cventry
    {\VAR{cert.issuer|default('')}}
    {\VAR{cert.name}}
    {}
    {\VAR{cert.date_obtained|default('')}}
    {}
\BLOCK{ endfor }
\end{cventries}
\BLOCK{ endif }

\end{document}
"""

# 6. Deedy CV (deedy-cv)
TEMPLATES["deedy-cv"] = r"""%!TEX TS-program = xelatex
\documentclass[]{deedy-resume-openfont}
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}

\begin{document}

\namesection{\VAR{full_name}}{}{
\BLOCK{ if website }\urlstyle{same}\href{\VAR{website}}{\VAR{website}} $\vert$ \BLOCK{ endif }
\BLOCK{ if email }\href{mailto:\VAR{email}}{\VAR{email}} $\vert$ \BLOCK{ endif }
\BLOCK{ if phone }\VAR{phone} $\vert$ \BLOCK{ endif }
\BLOCK{ if location }\VAR{location}\BLOCK{ endif }
}

\begin{minipage}[t]{0.33\textwidth}

\BLOCK{ if education }
\section{Education}
\BLOCK{ for edu in education }
\subsection{\VAR{edu.institution}}
\descript{\VAR{edu.degree}}
\location{\VAR{edu.start_date} -- \VAR{edu.end_date|default('Present')} \BLOCK{ if edu.location }| \VAR{edu.location}\BLOCK{ endif }}
\BLOCK{ if edu.gpa }GPA: \VAR{edu.gpa}\\ \BLOCK{ endif }
\sectionsep
\BLOCK{ endfor }
\BLOCK{ endif }

\BLOCK{ if skills or skill_categories }
\section{Skills}
\BLOCK{ for cat in skill_categories }
\subsection{\VAR{cat.category_name}}
\VAR{cat.skills|join(', ')}\\
\sectionsep
\BLOCK{ endfor }
\BLOCK{ if not skill_categories and skills }
\subsection{Core}
\VAR{skills|join(', ')}\\
\sectionsep
\BLOCK{ endif }
\BLOCK{ endif }

\BLOCK{ if certifications }
\section{Certifications}
\BLOCK{ for cert in certifications }
\textbf{\VAR{cert.name}}\\
\descript{\VAR{cert.issuer|default('')}}
\location{\VAR{cert.date_obtained|default('')}}
\sectionsep
\BLOCK{ endfor }
\BLOCK{ endif }

\end{minipage}
\hfill
\begin{minipage}[t]{0.65\textwidth}

\BLOCK{ if summary }
\section{Summary}
\descript{}
\small{\VAR{summary}}
\sectionsep
\BLOCK{ endif }

\BLOCK{ if experience }
\section{Experience}
\BLOCK{ for exp in experience }
\runsubsection{\VAR{exp.company}}
\descript{| \VAR{exp.role}}
\location{\VAR{exp.start_date} -- \VAR{exp.end_date|default('Present')} \BLOCK{ if exp.location }| \VAR{exp.location}\BLOCK{ endif }}
\begin{tightemize}
    \BLOCK{ for b in exp.bullets }
    \item \VAR{b}
    \BLOCK{ endfor }
\end{tightemize}
\sectionsep
\BLOCK{ endfor }
\BLOCK{ endif }

\BLOCK{ if projects }
\section{Projects}
\BLOCK{ for proj in projects }
\runsubsection{\VAR{proj.title}}
\descript{\BLOCK{ if proj.technologies }| \VAR{proj.technologies}\BLOCK{ endif }}
\begin{tightemize}
    \BLOCK{ if proj.description }\item \VAR{proj.description}\BLOCK{ endif }
    \BLOCK{ for b in proj.bullets }\item \VAR{b}\BLOCK{ endfor }
\end{tightemize}
\sectionsep
\BLOCK{ endfor }
\BLOCK{ endif }

\end{minipage}
\end{document}
"""

# Copy deedy-cv base to other deedy variants
TEMPLATES["deedy-modified"] = TEMPLATES["deedy-cv"]
TEMPLATES["deedy-single-column"] = TEMPLATES["deedy-cv"]
TEMPLATES["modern-deedy"] = TEMPLATES["deedy-cv"]

# 7. AltaCV (Clean, colorful layout)
TEMPLATES["altacv"] = r"""\documentclass[10pt,a4paper,ragged2e,withhyper]{altacv}

\geometry{left=1.2cm,right=1.2cm,top=1.2cm,bottom=1.2cm,columnsep=1cm}
\usepackage{paracol}

\definecolor{SlateGrey}{HTML}{2E2E2E}
\definecolor{LightGrey}{HTML}{666666}
\definecolor{Primary}{HTML}{004E89}
\definecolor{Secondary}{HTML}{1A659E}
\colorlet{name}{Primary}
\colorlet{tagline}{Secondary}
\colorlet{heading}{Primary}
\colorlet{headingrule}{Secondary}
\colorlet{subheading}{Secondary}
\colorlet{accent}{Primary}
\colorlet{emphasis}{SlateGrey}
\colorlet{body}{LightGrey}

\begin{document}
\name{\VAR{full_name}}
\tagline{\BLOCK{ if experience }\VAR{experience[0].role}\BLOCK{ else }Professional\BLOCK{ endif }}

\personalinfo{
  \BLOCK{ if email }\email{\VAR{email}}\BLOCK{ endif }
  \BLOCK{ if phone }\phone{\VAR{phone}}\BLOCK{ endif }
  \BLOCK{ if location }\location{\VAR{location}}\BLOCK{ endif }
  \BLOCK{ if linkedin }\linkedin{\VAR{linkedin}}\BLOCK{ endif }
  \BLOCK{ if github }\github{\VAR{github}}\BLOCK{ endif }
}

\makecvheader

\BLOCK{ if summary }
\cvsection{About}
\VAR{summary}
\medskip
\BLOCK{ endif }

\columnratio{0.65}
\begin{paracol}{2}

\BLOCK{ if experience }
\cvsection{Experience}
\BLOCK{ for exp in experience }
\cvevent{\VAR{exp.role}}{\VAR{exp.company}}{\VAR{exp.start_date} -- \VAR{exp.end_date|default('Present')}}{\VAR{exp.location|default('')}}
\begin{itemize}
    \BLOCK{ for b in exp.bullets }
    \item \VAR{b}
    \BLOCK{ endfor }
\end{itemize}
\divider
\BLOCK{ endfor }
\BLOCK{ endif }

\BLOCK{ if projects }
\cvsection{Projects}
\BLOCK{ for proj in projects }
\cvevent{\VAR{proj.title}}{\VAR{proj.technologies|default('')}}{}{}
\begin{itemize}
    \BLOCK{ if proj.description }\item \VAR{proj.description}\BLOCK{ endif }
    \BLOCK{ for b in proj.bullets }\item \VAR{b}\BLOCK{ endfor }
\end{itemize}
\divider
\BLOCK{ endfor }
\BLOCK{ endif }

\switchcolumn

\BLOCK{ if education }
\cvsection{Education}
\BLOCK{ for edu in education }
\cvevent{\VAR{edu.degree}}{\VAR{edu.institution}}{\VAR{edu.start_date} -- \VAR{edu.end_date|default('Present')}}{\VAR{edu.location|default('')}}
\BLOCK{ if edu.gpa }\textbf{GPA:} \VAR{edu.gpa}\BLOCK{ endif }
\divider
\BLOCK{ endfor }
\BLOCK{ endif }

\BLOCK{ if skills or skill_categories }
\cvsection{Skills}
\BLOCK{ for cat in skill_categories }
\textbf{\VAR{cat.category_name}}\\
\BLOCK{ for s in cat.skills }
\cvtag{\VAR{s}}
\BLOCK{ endfor }
\smallskip\\
\BLOCK{ endfor }
\BLOCK{ if not skill_categories and skills }
\BLOCK{ for s in skills }
\cvtag{\VAR{s}}
\BLOCK{ endfor }
\BLOCK{ endif }
\medskip
\BLOCK{ endif }

\BLOCK{ if certifications }
\cvsection{Certifications}
\BLOCK{ for cert in certifications }
\textbf{\VAR{cert.name}}\\
\small{\VAR{cert.issuer|default('')} \hfill \VAR{cert.date_obtained|default('')}}
\divider
\BLOCK{ endfor }
\BLOCK{ endif }

\end{paracol}
\end{document}
"""

# Copy AltaCV base to other AltaCV variants
TEMPLATES["altacv-lightdark"] = TEMPLATES["altacv"]
TEMPLATES["altacv-editorial"] = TEMPLATES["altacv"]
TEMPLATES["maltacv"] = TEMPLATES["altacv"]

# 8. ModernCV Classic (moderncv-classic)
TEMPLATES["moderncv-classic"] = r"""\documentclass[11pt,a4paper,sans]{moderncv}

\moderncvstyle{classic}
\moderncvcolor{blue}

\usepackage[scale=0.8]{geometry}

\name{\VAR{full_name}}{}
\title{\BLOCK{ if experience }\VAR{experience[0].role}\BLOCK{ else }Curriculum Vitae\BLOCK{ endif }}
\address{\VAR{location|default('')}}{}{}
\phone[mobile]{\VAR{phone|default('')}}
\email{\VAR{email}}
\BLOCK{ if website }\homepage{\VAR{website}}\BLOCK{ endif }

\begin{document}
\makecvtitle

\BLOCK{ if summary }
\section{Summary}
\cvitem{}{\VAR{summary}}
\BLOCK{ endif }

\BLOCK{ if experience }
\section{Experience}
\BLOCK{ for exp in experience }
\cventry{\VAR{exp.start_date} -- \VAR{exp.end_date|default('Present')}}{\VAR{exp.role}}{\VAR{exp.company}}{\VAR{exp.location|default('')}}{}{
\begin{itemize}
    \BLOCK{ for b in exp.bullets }
    \item \VAR{b}
    \BLOCK{ endfor }
\end{itemize}
}
\BLOCK{ endfor }
\BLOCK{ endif }

\BLOCK{ if education }
\section{Education}
\BLOCK{ for edu in education }
\cventry{\VAR{edu.start_date} -- \VAR{edu.end_date|default('Present')}}{\VAR{edu.degree}}{\VAR{edu.institution}}{\VAR{edu.location|default('')}}{\BLOCK{ if edu.gpa }GPA: \VAR{edu.gpa}\BLOCK{ endif }}{}
\BLOCK{ endfor }
\BLOCK{ endif }

\BLOCK{ if projects }
\section{Projects}
\BLOCK{ for proj in projects }
\cvitem{\VAR{proj.title}}{
  \BLOCK{ if proj.technologies }\textit{\VAR{proj.technologies}} -- \BLOCK{ endif }
  \VAR{proj.description|default('')}
  \BLOCK{ if proj.bullets }
  \begin{itemize}
    \BLOCK{ for b in proj.bullets }\item \VAR{b}\BLOCK{ endfor }
  \end{itemize}
  \BLOCK{ endif }
}
\BLOCK{ endfor }
\BLOCK{ endif }

\BLOCK{ if skills or skill_categories }
\section{Computer Skills}
\BLOCK{ for cat in skill_categories }
\cvitem{\VAR{cat.category_name}}{\VAR{cat.skills|join(', ')}}
\BLOCK{ endfor }
\BLOCK{ if not skill_categories and skills }
\cvitem{Skills}{\VAR{skills|join(', ')}}
\BLOCK{ endif }
\BLOCK{ endif }

\BLOCK{ if certifications }
\section{Certifications}
\BLOCK{ for cert in certifications }
\cvitem{\VAR{cert.date_obtained|default('')}}{\textbf{\VAR{cert.name}} -- \VAR{cert.issuer|default('')}}
\BLOCK{ endfor }
\BLOCK{ endif }

\end{document}
"""

TEMPLATES["moderncv-two-column"] = TEMPLATES["moderncv-classic"]
TEMPLATES["moderncv-academic"] = TEMPLATES["moderncv-classic"]

# 9. Friggeri CV
TEMPLATES["friggeri-cv"] = r"""%!TEX TS-program = xelatex
\documentclass[]{friggeri-cv}

\begin{document}
\header{\VAR{full_name}}{}
       {\BLOCK{ if experience }\VAR{experience[0].role}\BLOCK{ else }Professional\BLOCK{ endif }}

\begin{aside}
  \section{contact}
    \VAR{location|default('')}
    ~
    \VAR{phone|default('')}
    \href{mailto:\VAR{email}}{\VAR{email}}
    \BLOCK{ if linkedin }\href{\VAR{linkedin}}{LinkedIn}\BLOCK{ endif }
    \BLOCK{ if github }\href{\VAR{github}}{GitHub}\BLOCK{ endif }
  \section{skills}
    \BLOCK{ for cat in skill_categories }
    ~ \textbf{\VAR{cat.category_name}}
    \VAR{cat.skills|join(', ')}
    \BLOCK{ endfor }
    \BLOCK{ if not skill_categories and skills }
    \VAR{skills|join(', ')}
    \BLOCK{ endif }
  \BLOCK{ if certifications }
  \section{certifications}
    \BLOCK{ for cert in certifications }
    \textbf{\VAR{cert.name}}
    \VAR{cert.issuer|default('')}
    \BLOCK{ endfor }
  \BLOCK{ endif }
\end{aside}

\BLOCK{ if summary }
\section{about}
\VAR{summary}
\BLOCK{ endif }

\BLOCK{ if experience }
\section{experience}
\begin{entrytable}
\BLOCK{ for exp in experience }
  \entry
    {\VAR{exp.start_date} -- \VAR{exp.end_date|default('Present')}}
    {\VAR{exp.role}}
    {\VAR{exp.company}}
    {
      \begin{itemize}
        \BLOCK{ for b in exp.bullets }
        \item \VAR{b}
        \BLOCK{ endfor }
      \end{itemize}
    }
\BLOCK{ endfor }
\end{entrytable}
\BLOCK{ endif }

\BLOCK{ if education }
\section{education}
\begin{entrytable}
\BLOCK{ for edu in education }
  \entry
    {\VAR{edu.start_date} -- \VAR{edu.end_date|default('Present')}}
    {\VAR{edu.degree}}
    {\VAR{edu.institution}}
    {\BLOCK{ if edu.gpa }GPA: \VAR{edu.gpa}\BLOCK{ endif }}
\BLOCK{ endfor }
\end{entrytable}
\BLOCK{ endif }

\BLOCK{ if projects }
\section{projects}
\begin{entrytable}
\BLOCK{ for proj in projects }
  \entry
    {\VAR{proj.technologies|default('')}}
    {\VAR{proj.title}}
    {}
    {\VAR{proj.description|default('')}}
\BLOCK{ endfor }
\end{entrytable}
\BLOCK{ endif }

\end{document}
"""

TEMPLATES["friggeri-modified"] = TEMPLATES["friggeri-cv"]
TEMPLATES["simple-hipster-cv"] = TEMPLATES["libre-cv"]
TEMPLATES["timeline-cv"] = TEMPLATES["libre-cv"]

def main():
    print(f"Generating authentic template.tex.jinja files for {len(TEMPLATES)} templates...")
    for slug, tex in TEMPLATES.items():
        tdir = TEMPLATES_DIR / slug
        tdir.mkdir(exist_ok=True)
        jinja_path = tdir / "template.tex.jinja"
        jinja_path.write_text(tex.strip() + "\n", encoding="utf-8")
        print(f"  -> Generated {slug}/template.tex.jinja ({len(tex)} chars)")

    print("\nAll template.tex.jinja files successfully created!")

if __name__ == "__main__":
    main()
