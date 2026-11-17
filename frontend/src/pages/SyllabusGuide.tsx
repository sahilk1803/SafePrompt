import React, { useEffect, useState } from 'react';
import { BookOpen, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Badge } from '../components/ui/badge';

export const SyllabusGuide: React.FC = () => {
  const [data, setData] = useState<{ units: any[] } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getSyllabus().then((res) => {
      setData(res);
      setLoading(false);
    });
  }, []);

  if (loading || !data) {
    return <div className="h-40 rounded-xl bg-white border border-[#E2E8F0] animate-pulse" />;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-[26px] font-semibold tracking-tight text-[#0F172A]">
          Framework Reference
        </h1>
        <p className="text-[14px] text-[#64748B] mt-1">
          Overview of core responsible AI modules and conceptual coverage across the platform.
        </p>
      </div>

      <div className="space-y-4">
        {data.units.map((item, idx) => (
          <Card key={idx}>
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between gap-2">
                <CardTitle className="text-[15px]">{item.title}</CardTitle>
                <Badge variant="success">
                  <CheckCircle2 className="h-3 w-3" />
                  Implemented
                </Badge>
              </div>
              <CardDescription>{item.topics}</CardDescription>
            </CardHeader>
            <CardContent className="text-[13px] text-[#334155]">
              <div className="flex items-start gap-2 rounded-lg border border-[#E2E8F0] bg-[#F8FAFC] p-3">
                <BookOpen className="h-4 w-4 text-[#2563EB] shrink-0 mt-0.5" />
                <span>{item.implementation}</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};
