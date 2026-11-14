import type { WikiChallenge, WikiArticle } from '../types/game';

export const DAILY_CHALLENGES: WikiChallenge[] = [
  {
    id: 'challenge-1',
    title: 'Pop Royalty to Emperor of the French',
    startTitle: 'Taylor Swift',
    targetTitle: 'Napoleon',
    parHops: 3,
    hint: 'Look for cultural milestones, geography (France or Pennsylvania), or political magazines.',
  },
  {
    id: 'challenge-2',
    title: 'Blocky Worlds to the Roman Empire',
    startTitle: 'Minecraft',
    targetTitle: 'Julius Caesar',
    parHops: 3,
    hint: 'Swedish origins lead to European history, languages, or antiquity.',
  },
  {
    id: 'challenge-3',
    title: 'Pink Blockbuster to Nuclear Standoff',
    startTitle: 'Barbie (film)',
    targetTitle: 'Cold War',
    parHops: 2,
    hint: 'Cinema studio politics or American 20th-century history.',
  },
  {
    id: 'challenge-4',
    title: 'Crypto Frontier to Ancient Egypt',
    startTitle: 'Bitcoin',
    targetTitle: 'Cleopatra',
    parHops: 3,
    hint: 'Trace through the history of currency, precious metals, or the Mediterranean.',
  },
  {
    id: 'challenge-5',
    title: '8-Bit Plumber to the Renaissance Master',
    startTitle: 'Super Mario Bros.',
    targetTitle: 'Leonardo da Vinci',
    parHops: 3,
    hint: 'Italian heritage links directly to Florentine arts and inventions.',
  },
];

export const PRECACHED_ARTICLES: Record<string, WikiArticle> = {
  'Taylor Swift': {
    title: 'Taylor Swift',
    displayTitle: 'Taylor Swift',
    description: 'American singer-songwriter (born 1989)',
    extract:
      'Taylor Alison Swift is an American singer-songwriter. Recognized for her songwriting, musical versatility, and artistic reinventions, she is a prominent cultural figure of the 21st century.',
    thumbnail:
      'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/Taylor_Swift_at_the_2023_MTV_Video_Music_Awards_4.jpg/440px-Taylor_Swift_at_the_2023_MTV_Video_Music_Awards_4.jpg',
    outgoingLinks: [
      'Country music',
      'Pop music',
      'Grammy Awards',
      'Pennsylvania',
      'Nashville, Tennessee',
      'Time 100',
      'Time Person of the Year',
      'Rolling Stone',
      'Billboard 200',
      'Eras Tour',
      'United States',
      'France',
      'London',
    ],
    html: `
      <div class="wiki-prose">
        <p><strong>Taylor Alison Swift</strong> (born December 13, 1989) is an American singer-songwriter. Known for her autobiographical songwriting and cultural impact, she has received extensive media coverage across the globe.</p>
        <p>Born in West Reading, <a href="/wiki/Pennsylvania">Pennsylvania</a>, Swift moved to <a href="/wiki/Nashville,_Tennessee">Nashville, Tennessee</a> at age 14 to pursue a career in <a href="/wiki/Country_music">country music</a>. She signed with Big Machine Records in 2005 and released her eponymous debut album in 2006.</p>
        <p>Swift explored <a href="/wiki/Pop_music">pop music</a>, synth-pop, and alternative styles on albums such as <em>1989</em>, <em>Folklore</em>, and <em>Midnights</em>. She has won multiple <a href="/wiki/Grammy_Awards">Grammy Awards</a> and was honored as <a href="/wiki/Time_Person_of_the_Year">Time Person of the Year</a> in 2023. Her record-shaking global stadium tour, the <a href="/wiki/Eras_Tour">Eras Tour</a>, visited dozens of international destinations including Paris, <a href="/wiki/France">France</a> and London in the <a href="/wiki/United_Kingdom">United Kingdom</a>.</p>
      </div>
    `,
  },
  'Time Person of the Year': {
    title: 'Time Person of the Year',
    displayTitle: 'Time Person of the Year',
    description: 'Annual issue of the American news magazine Time',
    extract:
      'Person of the Year is an annual issue of the United States news magazine Time profiling the person, group, idea, or object that influenced the year the most.',
    thumbnail:
      'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Time_Magazine_logo.svg/440px-Time_Magazine_logo.svg.png',
    outgoingLinks: [
      'Time (magazine)',
      'United States',
      'Taylor Swift',
      'Franklin D. Roosevelt',
      'Winston Churchill',
      'Charles de Gaulle',
      'France',
      'Napoleon',
      'Adolf Hitler',
    ],
    html: `
      <div class="wiki-prose">
        <p><strong>Person of the Year</strong> is an annual issue of the <a href="/wiki/United_States">United States</a> news magazine <em>Time</em> that features and profiles a person, a group, an idea, or an object that "for better or for worse... has done the most to influence the events of the year".</p>
        <p>Past honorees have ranged from pop stars like <a href="/wiki/Taylor_Swift">Taylor Swift</a> to historic wartime statesmen such as <a href="/wiki/Franklin_D._Roosevelt">Franklin D. Roosevelt</a> and <a href="/wiki/Winston_Churchill">Winston Churchill</a>.</p>
        <p>Historical retrospectives published by the magazine have examined monumental leaders of modern statecraft, drawing comparisons between twentieth-century figures and foundational European empire builders like <a href="/wiki/Napoleon">Napoleon</a> and Charlemagne of <a href="/wiki/France">France</a>.</p>
      </div>
    `,
  },
  'France': {
    title: 'France',
    displayTitle: 'France',
    description: 'Country located primarily in Western Europe',
    extract:
      'France, officially the French Republic, is a country located primarily in Western Europe. Its capital and largest city is Paris.',
    thumbnail:
      'https://upload.wikimedia.org/wikipedia/en/thumb/c/c3/Flag_of_France.svg/440px-Flag_of_France.svg.png',
    outgoingLinks: [
      'Paris',
      'French Revolution',
      'Napoleon',
      'French language',
      'European Union',
      'Eiffel Tower',
      'Louvre',
      'Louis XIV',
    ],
    html: `
      <div class="wiki-prose">
        <p><strong>France</strong>, officially the <strong>French Republic</strong>, is a country located primarily in Western Europe. Its capital and largest city is <a href="/wiki/Paris">Paris</a>, a major global center of art, science, philosophy, and economy.</p>
        <p>Following the upheaval of the <a href="/wiki/French_Revolution">French Revolution</a> in 1789, the nation transformed rapidly into the First French Empire under the military brilliance of <a href="/wiki/Napoleon">Napoleon</a> Bonaparte, whose campaigns reshaped the political landscape of Europe.</p>
        <p>Notable French architectural landmarks include the <a href="/wiki/Eiffel_Tower">Eiffel Tower</a>, the Palace of Versailles built by <a href="/wiki/Louis_XIV">Louis XIV</a>, and the <a href="/wiki/Louvre">Louvre</a> Museum.</p>
      </div>
    `,
  },
  'Napoleon': {
    title: 'Napoleon',
    displayTitle: 'Napoleon Bonaparte',
    description: 'French military commander and Emperor of the French (1769–1821)',
    extract:
      'Napoleon Bonaparte was a French military commander and political leader who rose to prominence during the French Revolution and led successful campaigns during the Revolutionary Wars.',
    thumbnail:
      'https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Jacques-Louis_David_-_The_Emperor_Napoleon_in_His_Study_at_the_Tuileries_-_Google_Art_Project.jpg/440px-Jacques-Louis_David_-_The_Emperor_Napoleon_in_His_Study_at_the_Tuileries_-_Google_Art_Project.jpg',
    outgoingLinks: [
      'France',
      'French Revolution',
      'Napoleonic Wars',
      'Battle of Waterloo',
      'Corsica',
      'Paris',
    ],
    html: `
      <div class="wiki-prose">
        <p><strong>Napoleon Bonaparte</strong> (born Napoleone Buonaparte; 15 August 1769 – 5 May 1821) was a French military commander and political leader who rose to prominence during the <a href="/wiki/French_Revolution">French Revolution</a>.</p>
        <p>Born on the island of <a href="/wiki/Corsica">Corsica</a>, he rose rapidly through the ranks of the French military and became Emperor of the French in 1804. He fought dozens of major engagements during the Napoleonic Wars before his eventual defeat at the <a href="/wiki/Battle_of_Waterloo">Battle of Waterloo</a> in 1815.</p>
      </div>
    `,
  },
};
