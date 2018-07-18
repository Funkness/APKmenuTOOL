#pragma once
#include "zip.h"
#include "unzip.h"
#include <list>
#include<atlstr.h>
using namespace std;
using namespace ATL;


class CZipFunction
{
	public:
		// ------------------------------------------------------------------------------------------------------------------------
		// Summary:
		//   ��ѹzip�ļ���ָ��·��, �����ؽ�ѹ�ļ�·�����ļ�����
		// Parameters:
		//   lpszZipFullName   - ����ѹ zipѹ���������ļ���·����zipѹ������; ��"D://00//1.zip"��
		//   lpszUnZipPath     - ��ѹ�������ļ� �����λ�õ�����·��; �� ��D://01��
		//   szPackageName     - apk ����  
		//   fileName          - apk���ļ��б�
		//   fileType          - ƥ������
		// Returns:
		//   ��ѹ�ɹ�����ZR_OK����ѹʧ�ܷ��ش����롣
		// ------------------------------------------------------------------------------------------------------------------------

		static ZRESULT ExtractApkToDir(LPCTSTR lpszZipFullName, LPCTSTR lpszUnZipPath,CString szPackageName,list<CString>& fileName,LPCTSTR fileType);

		// ------------------------------------------------------------------------------------------------------------------------
		// Summary:
		//   ѹ��ָ��·���µ��ļ���������ѹ������ָ��·����
		// Parameters:
		//   lpszSrcPath        - ��ѹ���ļ����ڵ�·��; ��"D://00"��
		//   lpszDestPath       - ѹ����ɺ󣬴��ѹ������·����
		//                        �˲���ʡ��ʱ��Ĭ�ϴ��·��Ϊexe���������ļ���·����
		//   lpszZipName        - ѹ����ɺ�ѹ�������ƣ��硰MySkin.zip����
		// Returns:
		//   ѹ���ɹ�����ZR_OK��ѹ��ʧ�ܷ��ش����롣
		// ------------------------------------------------------------------------------------------------------------------------
		static ZRESULT CompressDirToZip(LPCTSTR lpszSrcPath, LPCTSTR lpszZipName, LPCTSTR lpszDestPath = NULL);

		// ------------------------------------------------------------------------------------------------------------------------
		// Summary:
		//   ѹ��ָ��·���µ��ļ���������ѹ������ָ��·����
		// Parameters:
		//   lpszSrcPath        - ��ѹ���ļ����ڵ�·��; ��"D://00"��
		//   lpszZipName        - ѹ����ɺ�ѹ�������ƣ��硰MySkin.zip����
		//   hz                 -HZIP���
		//   lpszDestPath       - ѹ����ɺ󣬴��ѹ������·����
		//                        �˲���ʡ��ʱ��Ĭ�ϴ��·��Ϊexe���������ļ���·����
		// Returns:
		//   ѹ���ɹ�����ZR_OK��ѹ��ʧ�ܷ��ش����롣
		// ------------------------------------------------------------------------------------------------------------------------
		static ZRESULT DirToZip(LPCTSTR lpszSrcPath, LPCTSTR lpszZipName, HZIP& hz, LPCTSTR lpszDestPath);
};