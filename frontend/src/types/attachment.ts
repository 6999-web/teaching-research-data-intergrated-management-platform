// Attachment types
export interface Attachment {
  id?: string;
  evaluation_id?: string;
  evaluationId?: string;
  indicator: string; // 考核指标
  file_name?: string;
  fileName?: string;
  file_size?: number;
  fileSize?: number;
  file_type?: string;
  fileType?: string;
  storage_path?: string;
  storagePath?: string;
  classified_by?: 'user' | 'ai';
  classifiedBy?: 'user' | 'ai';
  uploaded_at?: string;
  uploadedAt?: string;
  is_archived?: boolean;
  isArchived?: boolean;
  archived_at?: string;
  archivedAt?: string;
}

// Attachment with relations (includes teaching office and evaluation info)
export interface AttachmentWithRelations extends Attachment {
  teaching_office_id?: string;
  teaching_office_name?: string;
  evaluation_year?: number;
}

export interface AttachmentUploadData {
  evaluationId: string;
  indicator: string;
  files: File[];
}

export interface UploadProgress {
  fileName: string;
  percentage: number;
  status: 'uploading' | 'success' | 'error';
}

// 考核指标类型
export type IndicatorType = 'teaching_reform_projects' | 'honorary_awards' | 'course_construction' | 'teaching_quality' | 'student_guidance' | 'scientific_research' | 'team_building';

// 考核指标配置
export interface IndicatorConfig {
  key: IndicatorType;
  label: string;
  description: string;
  fileTypes: string[]; // 支持的文件类型
  category: 'certificate' | 'project'; // 证书类或项目类
}

// 预定义的考核指标
export const INDICATORS: IndicatorConfig[] = [
  {
    key: 'teaching_reform_projects',
    label: '教学改革项目',
    description: '教学改革项目相关证书、立项文件等',
    fileTypes: ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'],
    category: 'project'
  },
  {
    key: 'honorary_awards',
    label: '荣誉表彰',
    description: '荣誉证书、表彰文件等',
    fileTypes: ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'],
    category: 'certificate'
  },
  {
    key: 'course_construction',
    label: '课程建设',
    description: '课程建设相关材料',
    fileTypes: ['pdf', 'doc', 'docx', 'ppt', 'pptx'],
    category: 'project'
  },
  {
    key: 'teaching_quality',
    label: '教学质量',
    description: '教学质量评估材料',
    fileTypes: ['pdf', 'doc', 'docx', 'xls', 'xlsx'],
    category: 'project'
  },
  {
    key: 'student_guidance',
    label: '学生指导',
    description: '学生指导相关材料',
    fileTypes: ['pdf', 'doc', 'docx'],
    category: 'project'
  },
  {
    key: 'scientific_research',
    label: '科研工作',
    description: '科研成果、论文等材料',
    fileTypes: ['pdf', 'doc', 'docx'],
    category: 'project'
  },
  {
    key: 'team_building',
    label: '团队建设',
    description: '团队建设相关材料',
    fileTypes: ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'],
    category: 'project'
  }
];
