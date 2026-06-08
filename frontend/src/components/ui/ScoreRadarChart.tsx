import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip } from 'recharts';

interface ScoreRadarProps {
  scores: {
    tfidf_similarity?: number;
    skill_match: number;
    section_coverage: number;
    keyword_density: number;
    quality: number;
    ats_compatibility: number;
  }
}

export const ScoreRadarChart = ({ scores }: ScoreRadarProps) => {
  const data = [
    { subject: 'Semantic Match', A: scores.tfidf_similarity || 0, fullMark: 100 },
    { subject: 'Skills', A: scores.skill_match, fullMark: 100 },
    { subject: 'Sections', A: scores.section_coverage, fullMark: 100 },
    { subject: 'Keywords', A: scores.keyword_density, fullMark: 100 },
    { subject: 'Quality', A: scores.quality, fullMark: 100 },
    { subject: 'ATS Fit', A: scores.ats_compatibility, fullMark: 100 },
  ];

  return (
    <div className="w-full h-80 flex flex-col items-center justify-center">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="75%" data={data}>
          <PolarGrid stroke="rgba(255,255,255,0.1)" />
          <PolarAngleAxis dataKey="subject" tick={{ fill: 'rgba(255,255,255,0.6)', fontSize: 13 }} />
          <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
          <Tooltip 
            contentStyle={{ backgroundColor: 'rgba(15,23,42,0.9)', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '12px' }}
            itemStyle={{ color: '#00D1FF', fontWeight: 'bold' }}
            formatter={(value: any) => [`${Number(value).toFixed(1)}%`, 'Score']}
          />
          <Radar name="Score" dataKey="A" stroke="#00D1FF" strokeWidth={2} fill="#00D1FF" fillOpacity={0.3} />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
};
